import time
import sys
import selectors
import bisect


class EventLoop(object):
    def __init__(self,*task):
        self._running = False
        self._stdin_handles = []
        self._timers = []
        self.selector = selectors.DefaultSelector()
        self.selector.register(sys.stdin,selectors.EVENT_READ)

    def run_forever(self):
        self._running = True
        while self._running:
            for event,mask in self.selector.select(0):
                line = event.fileobj.readline().strip()
                for callback in self._stdin_handles:
                    callback(line)

            while self._timers and self._timers[0][0] < time.time():
                handle = self._timers[0][1]
                del self._timers[0]
                handle()

    def add_stdin_handle(self,callback):
        self._stdin_handles.append(callback)

    def add_timer(self,wait_time,callback):
        bisect.insort(self._timers,(time.time()+wait_time,callback))

    def stop(self):
        self._running = False

def main():
    loop = EventLoop()
    def on_stdin_input(line):
        if line == "exit":
            loop.stop()
            return
        n = int(line)
        print("input num is {}".format(n))


    def hello_world():
        print("{} is time and print {}".format(time.time(),"hello_world"))
        loop.add_timer(3,hello_world)

    loop.add_stdin_handle(on_stdin_input)
    loop.add_timer(0,hello_world)
    loop.run_forever()


if __name__=='__main__':
    main()
