#!/usr/bin/env python
import os
import sys
import resource
import time
import signal
import util


def exit_gracefully():
    sys.exit()


def terminate_handler(signum, frame):
    exit_gracefully()


def set_up():  # Return the FD of the log file
    os.closerange(3, resource.RLIMIT_NOFILE)
    new_directory = os.open("/dev/null", os.O_RDWR)
    for x in range(3):
        os.dup2(new_directory, x)
    os.chdir("/")
    signal.signal(signal.SIGINT, terminate_handler)
    signal.signal(signal.SIGTERM, terminate_handler)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGUSR1, proc_child_restarter)


def proc_child_restarter(signum, frame):
    signal.setitimer(signal.ITIMER_REAL, sys.maxsize)


def time_left():
    return int(signal.getitimer(signal.ITIMER_REAL))[0]


def proc_child():
    signal.signal(signal.SIGALRM, signal.SIG_IGN)
    try:
        with os.open("log_file.txt", os.O_CREAT | os.O_WRONLY | os.O_APPEND) as log_fd:
            while True:
                time.sleep(1)
                util.write_to_target(log_fd, str(sys.maxsize - time_left()))
    except Exception as e:
        with os.open("log_file.txt", os.O_WRONLY | os.O_APPEND) as log_fd:
            util.write_to_target(log_fd, "Error! %s" % e)


def main():
    child = os.fork()
    if child == 0:
        set_up()
        proc_child()
    os._exit(0)


if __name__ == "__main__":
    main()
