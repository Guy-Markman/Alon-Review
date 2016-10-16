#!/usr/bin/env python
import os
import sys
import resource
import time
import signal
import util


def exit_gracefully():
    os.closerange(3, resource.RLIMIT_NOFILE)
    sys.exit()


def terminate_handler(signum, frame):
    exit_gracefully()


def set_up():  # Return the FD of the log file
    new_directory = os.open("/dev/null", os.O_RDWR)
    for x in range(3):
        os.dup2(new_directory, x)
    os.chdir("/")
    log_fd = os.open("log_file.txt", os.O_CREAT | os.O_WRONLY)
    signal.signal(signal.SIGINT, terminate_handler)
    signal.signal(signal.SIGTERM, terminate_handler)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    return log_fd


def proc_child_restarter(signum, frame):
    signal.setitimer(signal.ITIMER_REAL, sys.maxint)


def time_left():
    return int(signal.getitimer(signal.ITIMER_REAL))[0]


def proc_child(log_fd):
    signal.signal(signal.SIGALRM, signal.SIG_IGN)
    while True:
        time.sleep(1)
        util.write_to_target(log_fd, str(sys.maxint - time_left()))


def main():
    log_fd = set_up()
    child = os.fork()
    if child == 0:
        signal.signal(signal.SIGUSR1, proc_child_restarter)
        proc_child(log_fd)
    os._exit(0)


if __name__ == "__main__":
    main()
