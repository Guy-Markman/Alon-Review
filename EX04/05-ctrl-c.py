#!/usr/bin/env python
import signal
import util
import time


def hal9000(signum, frame):
    util.write_to_target(1, "I'm sorry Dave, I'm afraid I can't do that\n")


def main():
    signal.signal(signal.SIGINT, hal9000)
    while True:
        time.sleep(86400)  # Once every day


if __name__ == '__main__':
    main()
