#!/usr/bin/env python
import constants
import contextlib
import mmap
import os
import time
import util


def proc_child(file):
    while True:
        util.write_to_target(
            1,
            "%s\n" % file[constants.START_LOCATION:constants.END_LOCATION]
        )
        time.sleep(2)


def proc_parent(file):
    counter = 0
    while True:
        file[constants.START_LOCATION:constants.END_LOCATION] = "%04x" % (
            counter)
        counter += 1
        time.sleep(1)


def main():
    with contextlib.closing(mmap.mmap(-1, constants.FILE_SIZE)) as mm:
        child = os.fork()
        if child == 0:
            proc_child(mm)
        else:
            proc_parent(mm)


if __name__ == "__main__":
    main()
