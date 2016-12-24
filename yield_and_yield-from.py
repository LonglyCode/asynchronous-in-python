import random

import asyncio


def fibonacci():
    a = b = 1
    yield a
    yield b
    while True:
        a,b = b,a+b
        yield b

def fib(n):
    rv = 0
    gen = fibonacci()
    while rv < n:
        rv = next(gen)
        print("result is %d"%(rv))

# consume and produce
def consume():
    total = 0.0
    count = 0
    average = None
    while True:
        data = yield
        if data is None:
            break
        total += data
        count += 1
        average = total/count
        print('Consumed, average data is %d'%data)

def produce(consumer,n):
    consumer.send(None)
    produces = random.sample(range(9),n)
    while produces:
        data = produces.pop()
        print('produce %d'%data)
        consumer.send(data)
    consumer.close()

def fibonacci2(n):
    a = b = 1
    yield a
    yield b
    while b < n:
        a,b = b,a+b
        yield b

def fib_from():
    yield from fibonacci2(100)

def simple_yield():
    for s in "allisdone":
        yield s
    for i in range(1,9):
        yield i

def simple_yield_from():
    yield from "allisdone"
    yield from range(1,9)

def main():
    yield from fib_from()
    yield from simple_yield_from()

if __name__=='__main__':
    print(list(main()))
