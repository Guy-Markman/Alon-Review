#!/usr/bin/env python
import os
import time
import sys
import util
import signal

TIME_SLEEP_CHILD = 2
TIME_SLEEP_PARENT = 60


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
    t = time.time()
    util.sleep(TIME_SLEEP_PARENT)
    sys.exit()


def handler(signum, frame):
    os.wait()


def main():
    signal.signal(signal.SIGCHLD, handler)
    child = os.fork()
    if child == 0:
        child_process()
    else:
        parent_process(child)


if __name__ == "__main__":
    main()
