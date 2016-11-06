#!/usr/bin/env python
import os
import sys
import resource
import signal
import util
import time
import stat


counter = 0
run = True


def terminate_handler(signum, frame):
    global run
    run = False


def reset_handler(signum, frame):
    global counter
    counter = 0


def add_handler(signum, frame):
    global counter
    counter += 1


def set_up():
    os.closerange(3, 3+resource.RLIMIT_NOFILE)
    new_directory = os.open(os.devnull, os.O_RDWR)
    try:
        for x in range(3):
            os.dup2(new_directory, x)
    finally:
        os.close(new_directory)
    os.chdir("/")
    signal.signal(signal.SIGINT, terminate_handler)
    signal.signal(signal.SIGTERM, terminate_handler)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)


def proc_child():
    signal.signal(signal.SIGUSR1, reset_handler)
    signal.signal(signal.SIGALRM, add_handler)
    signal.alarm(1)
    global counter
    global run
    log_fd = os.open(
                    "log_file.txt",
                    os.O_CREAT | os.O_APPEND | os.O_WRONLY,
                    stat.S_IREAD | stat.S_IWRITE | stat.S_IRGRP | stat.S_IROTH
                    )
    last = -1
    try:
        while run:
            if counter != last:
                util.write_to_target(log_fd, str(counter))
                last = counter
                signal.alarm(1)
            time.sleep(86400)
    except Exception as e:
        util.write_to_target(log_fd, "Error! %s" % e)
    finally:
        os.close(log_fd)
    sys.exit()


def main():
    child = os.fork()
    if child != 0:
        os._exit(0)
    set_up()
    proc_child()


if __name__ == "__main__":
    main()
