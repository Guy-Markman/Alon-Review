#!/usr/bin/env python
import os
import sys
import resource
import signal
import util


def set_ign(signum, frame):
    signal.signal(signum, signal.SIG_IGN)


def set_up():
    os.closerange(3, resource.RLIMIT_NOFILE)
    new_directory = os.open("/dev/null", os.O_WRONLY)
    try:
        for x in range(3):
            os.dup2(new_directory, x)
    finally:
        os.close(new_directory)
    os.chdir("/")
    signal.signal(signal.SIGINT, set_ign)
    signal.signal(signal.SIGTERM, set_ign)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGUSR1, set_ign)
    signal.signal(signal.SIGALRM, set_ign)


def proc_child():
    counter = 0
    log_fd = os.open("log_file.txt", os.O_CREAT | os.O_APPEND, 00777)
    try:        
        while True:
            if signal.getsignal(
                    signal.SIGINT) is signal.SIG_IGN or signal.getsignal(
                    signal.SIGTERM) is signal.SIG_IGN:
                break
            if signal.getsignal(signal.SIGALRM) is signal.SIG_IGN:
                util.write_to_target(log_fd, str(counter))
                counter += 1
                signal.signal(signal.SIGALRM, set_none)
                signal.alarm(1)
            if signal.getsignal(signal.SIGUSR1) is signal.SIG_IGN:
                counter = 0
                signal.signal(signal.SIGUSR1, set_none)

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
