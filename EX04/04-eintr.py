#!/usr/bin/env python
# EINTR error code
import os
import sys
import util
import signal

TIME_SLEEP_CHILD = 2
TIME_SLEEP_PARENT = 60

BUFF_SIZE = 1000


def child_process():
    time.sleep(TIME_SLEEP_CHILD)
    sys.exit()


def parent_process(child_pid):
    util.write_to_target(
        1, (
                "Parent pid: %s\n"
                "Child pid: %s\n"
            ) % (
                    os.getpid(),
                    child_pid
                )
        )
    util.read_from_target(0, BUFF_SIZE)
    sys.exit()


def handler_SIGCHLD(signum, frame):
    os.wait()


def handler_SIGALRM(signum, frame):
    print "waiting"
    signal.alarm(1)


def init_signals():
    signal.signal(signal.SIGALRM, handler_SIGALRM)
    signal.alarm(1)
    signal.signal(signal.SIGCHLD, handler_SIGCHLD)


def main():
    init_signals()
    child = os.fork()
    if child == 0:
        child_process()
    parent_process(child)


if __name__ == "__main__":
    main()
