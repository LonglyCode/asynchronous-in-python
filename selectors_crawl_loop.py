import socket
import time

from selectors import EVENT_READ, EVENT_WRITE, DefaultSelector


class Timeout(Exception):
    pass

class Future:
    def __init__(self):
        self.result = None
        self._callbacks = []

    def result(self):
        return self.result

    def add_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result):

        self.result = result
        for fn in self._callbacks:
            fn(self)

    def __iter__(self):
        yield self
        return self.result


class Task:
    def __init__(self, coro):
        self.coro = coro
        f = Future()
        f.set_result(None)
        self.step(f)

    def step(self, future):

        try:
            next_future = self.coro.send(future.result)
        except StopIteration:
            return

        next_future.add_done_callback(self.step)

selector = DefaultSelector()

class EventLoop(object):
    stopped = False

    def __init__(self):
        """

        """
        self._selector = selector

    def register(self,fd,event,callback):
        self._selector.register(fd,event,callback)

    def unregister(self,fd):
        self._selector.unregister(fd)

    def run_forever(self,coros):
        tasks = [Task(coro) for coro in coros]
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
                callback = event_key.data
                callback()

    def stop(self):
        self.stopped = True

def read(sock):
    f = Future()

    def on_readable():
        f.set_result(sock.recv(4096))

    selector.register(sock.fileno(), EVENT_READ, on_readable)
    chunk = yield from f
    selector.unregister(sock.fileno())
    return chunk

def read_all(sock):
    response = []
    chunk = yield from read(sock)
    while chunk:
        response.append(chunk)
        chunk = yield from read(sock)

    return b''.join(response)

class AsyncClient(object):

    def __init__(self,loop):

        self._loop = loop
        self.response = None

    def fetch(self,url):
        sock = socket.socket()

        yield from self._connect(sock,('www.baidu.com', 80))
        get = 'GET {} HTTP/1.0\r\nHost: www.baidu.com\r\n\r\n'.format(url)
        sock.send(get.encode('ascii'))
        # TODO how to let read_all function become a inline method?
        self.response = yield from read_all(sock)
        print(self.response)

    def _connect(self,sock,address):

        f = Future()
        def on_connected():
            f.set_result(None)

        sock.setblocking(False)
        try:
            sock.connect(address)
        except BlockingIOError:
            pass
        self._loop.register(sock.fileno(),EVENT_WRITE,on_connected)
        yield from f
        self._loop.unregister(sock.fileno())


def main():
    loop = EventLoop()
    req = AsyncClient(loop=loop)
    loop.run_forever([req.fetch('/s?wd={}'.format(i)) for i in range(100)])
    loop.stop()

if __name__=='__main__':
    main()
