import time
import sys
import threading
import selectors


def hello_world():
    print("{} is time and print {}".format(time.time(),"hello_world"))


def process_input(stream):
    text = stream.readline()
    n = int(text.strip())
    print("input num is {}".format(n))


def main():
    selector = selectors.DefaultSelector()
    selector.register(sys.stdin,selectors.EVENT_READ)
    last_hello = 0
    while 1:
        for event,mask in selector.select(0.1):
            process_input(event.fileobj)
        if time.time() - last_hello > 3:
            last_hello = time.time()
            hello_world()

if __name__=='__main__':
    main()
