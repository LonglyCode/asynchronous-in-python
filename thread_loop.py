import time
import sys
import threading


def hello_world():
    while 1:
        print "{} is time and print {}".format(time.time(),"hello_world")
        time.sleep(3)


def read_and_process_input():
    while 1:
        n = int(input())
        print "input num is {}".format(n)

def main():
    t = threading.Thread(target=hello_world)
    t.daemon = True
    t.start()
    read_and_process_input()

if __name__=='__main__':
    main()
