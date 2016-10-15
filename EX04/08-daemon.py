#!/usr/bin/env python
import os
import sys
import resource
import time
import signal
import util


def terminate_handler(signum, frame):
    sys.exit()


def set_up():
    os.closerange(3, resource.RLIMIT_NOFILE)
    new_directory = os.open("/dev/null", os.O_RDWR)
    for x in range(3):
        os.dup2(new_directory, x)
    os.chdir("/")
    signal.signal(signal.SIGINT, terminate_handler)
    signal.signal(signal.SIGTERM, terminate_handler)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)


def proc_child():
    counter = 0
    while True:
        time.sleep(1)
        util.write_to_target(1, str(counter))
        counter += 1


def main():
    set_up()
    child = os.fork()
    if child == 0:
        signal.signal(signal.SIGUSR1, proc_child)
        proc_child()
    os._exit(0)


if __name__ == "__main__":
    main()
