#!/usr/bin/env python
import constants
import contextlib
import mmap
import os
import time
import util


def main():
    fd = os.open(constants.BACKUP_FILE, os.O_RDWR)
    try:
        with contextlib.closing(mmap.mmap(fd, 0)) as mm:
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
