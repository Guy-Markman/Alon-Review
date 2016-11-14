#!/usr/bin/env python
import constants
import contextlib
import mmap
import os
import sys
import time
import util


def proc_child(file):
    while True:
        util.write_to_target(
            1,
            "%s\n" % file[constants.START_LOCATION:constants.END_LOCATION]
        )
        time.sleep(2)
        sys.close()


def proc_parent(file):
    counter = 0
    while True:
        hex_counter = hex(counter)
        file[
            constants.START_LOCATION:constants.START_LOCATION +
            len(hex_counter)] = hex_counter
        counter += 1
        time.sleep(1)
        sys.close()


def main():
    fd = os.open(constants.BACKUP_FILE, os.O_RDWR)
    try:
        mm = mmap.mmap(fd, 0)
        with contextlib.closing(mm):
            while True:
                util.write_to_target(
                    1,
                    "%s\n" % mm[
                        constants.START_LOCATION:constants.END_LOCATION])
                time.sleep(2)

    finally:
        os.close(fd)


if __name__ == "__main__":
    main()
