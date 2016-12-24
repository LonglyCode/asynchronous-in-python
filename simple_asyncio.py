import heapq
import socket
import time
from collections import deque

from selectors import EVENT_READ, EVENT_WRITE, DefaultSelector

selector = DefaultSelector()


class Timeout(Exception):
    pass


class Handle(object):
    def __init__(self, func, args):
        self.func = func
        self.args = args

    def run(self):
        self.func(self.args)


class TimeHanle(Handle):
    def __init__(self, when, func, args):
        super(TimeHanle, self).__init__(func, args)
        self._when = when

    def __lt__(self, other):
        return self._when < other._when

    def __eq__(self, other):
        if isinstance(other, TimerHandle):
            return self._when == other._when


class Future:
    def __init__(self):
        self._result = None
        self._callbacks = []

    def result(self):
        return self._result

    def add_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result):

        self._result = result
        for fn in self._callbacks:
            fn(self)

    def __iter__(self):
        yield self
        return self._result


class Task:
    def __init__(self, coro, loop):
        self.coro = coro
        self._loop = loop
        self._loop.call_soon(self.step)

    def step(self, value=None):

        try:
            next_future = self.coro.send(value)
        except StopIteration:
            return

        if isinstance(next_future, Future):
            next_future.add_done_callback(self.wakeup)

    def wakeup(self, future):
        value = future.result()
        if value:
            self.step(value)


class EventLoop(object):

    stopped = False

    def __init__(self):
        self._selector = selector
        self._reader = deque()
        self._scheduled = []

    def call_soon(self, callback, *args):
        handle = Handle(callback, args)
        self._ready.append(handle)
        return handle

    def call_later(self, delay, callback, *args):
        when = time.time() + delay
        timer = TimerHandle(when, callback, args)
        heapq.heappush(self._scheduled, timer)
        return timer

    def _add_callback(self, handle):
        if isinstance(handle, TimerHandle):
            heapq.heappush(self._scheduled, handle)
        else:
            self._ready.append(handle)

    def add_reader(self, fd, callback, *args):
        handle = Handle(callback, args)
        try:
            key = self._selector.get_key(fd)
        except KeyError:
            self._selector.register(fd, selectors.EVENT_READ, (handle, None))
        else:
            mask, (reader, writer) = key.events, key.data
            self._selector.modify(fd, mask | selectors.EVENT_READ,
                                  (handle, writer))

    def remove_reader(self, fd):
        try:
            key = self._selector.get_key(fd)
        except KeyError:
            return False
        else:
            mask, (reader, writer) = key.events, key.data
            mask &= ~selectors.EVENT_READ
            if not mask:
                self._selector.unregister(fd)
            else:
                self._selector.modify(fd, mask, (None, writer))

    def add_writer(self, fd, callback, *args):
        handle = events.make_handle(callback, args)
        try:
            key = self._selector.get_key(fd)
        except KeyError:
            self._selector.register(fd, selectors.EVENT_WRITE, (None, handle))
        else:
            mask, (reader, writer) = key.events, key.data
            self._selector.modify(fd, mask | selectors.EVENT_WRITE,
                                  (reader, handle))

    def remove_writer(self, fd):
        try:
            key = self._selector.get_key(fd)
        except KeyError:
            return False
        else:
            mask, (reader, writer) = key.events, key.data
            mask &= ~selectors.EVENT_WRITE
            if not mask:
                self._selector.unregister(fd)
            else:
                self._selector.modify(fd, mask, (reader, None))

    def run_forever(self, coros):
        tasks = [Task(coro, self) for coro in coros]
        try:
            self._run()
        except Exception as e:
            print(e)
            return

    def _run(self):
        while not self.stopped:
            events = self._selector.select(5)
            if not events:
                raise Timeout("time out!!")
            for event_key, event_mask in events:
                fileobj, (reader, writer) = key.fileobj, key.data
                if mask & selectors.EVENT_READ and reader is not None:
                    self._add_callback(reader)
                if mask & selectors.EVENT_WRITE and writer is not None:
                    self._add_callback(writer)

            now = time.time()
            while self._scheduled:
                handle = self._scheduled[0]
                if handle._when > now:
                    break
                handle = heapq.heappop(self._scheduled)
                self._ready.append(handle)

            ntodo = len(self._ready)
            for i in range(ntodo):
                handle = self._ready.popleft()
                handle.run()
                handle = None

    def stop(self):
        self.stopped = True


class AsyncClient(object):
    def __init__(self, loop):

        self._loop = loop
        self.response = None

    def fetch(self, url):

        sock = socket.socket()

        yield from self._connect(sock, ('www.baidu.com', 80))
        get = 'GET {} HTTP/1.0\r\nHost: www.baidu.com\r\n\r\n'.format(url)
        sock.send(get.encode('ascii'))
        # TODO how to let read_all function become a inline method?
        self.response = yield from self.read_all(sock)

        print(self.response)

    def read(self, sock):
        f = Future()

        def on_readable():
            f.set_result(sock.recv(4096))

        self._loop.selector.register(sock.fileno(), EVENT_READ, on_readable)
        chunk = yield from f
        self._loop.selector.unregister(sock.fileno())
        return chunk

    def read_all(self, sock):
        response = []
        chunk = yield from self.read(sock)
        while chunk:
            response.append(chunk)
            chunk = yield from self.read(sock)

        return b''.join(response)

    def _connect(self, sock, address):

        f = Future()

        def on_connected():
            f.set_result(None)

        sock.setblocking(False)
        try:
            sock.connect(address)
        except BlockingIOError:
            pass
        self._loop.register(sock.fileno(), EVENT_WRITE, on_connected)
        yield from f
        self._loop.unregister(sock.fileno())


def main():
    loop = EventLoop()
    req = AsyncClient(loop=loop)
    loop.run_forever([req.fetch('/s?wd={}'.format(i)) for i in range(100)])
    loop.stop()


if __name__ == '__main__':
    main()
