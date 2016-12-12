import time
import sys
# import selectors

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

class Task:
    def __init__(self, coro):
        self.coro = coro
        f = Future()
        f.set_result(None)
        self.step(f)

    def step(self, future):
        print("enter step")
        try:
            next_future = self.coro.send(future.result)
        except StopIteration:
            return

        next_future.add_done_callback(self.step)

def read():
    future = Future()
    print("read start")
    yield future
    print("read stop")
    return


if __name__=='__main__':
    r = read()
    Task(r)
    f = r.gi_frame.f_code['future']
    f.set_result(None)
