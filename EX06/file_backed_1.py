#!/usr/bin/env python
import constants
import contextlib
import mmap
import os
import stat
import time

FILE_END = "\0"


def main():
    fd = os.open(
        constants.BACKUP_FILE,
        os.O_CREAT | os.O_RDWR,
        stat.S_IREAD | stat.S_IWRITE | stat.S_IRGRP | stat.S_IROTH
    )
    while os.fstat(fd).st_size < constants.FILE_SIZE:
        os.write(fd, FILE_END)
    try:
        with contextlib.closing(mmap.mmap(fd, constants.FILE_SIZE)) as mm:
            counter = 0
            while True:
                mm[
                    constants.START_LOCATION:
                    constants.END_LOCATION
                ] = "%*x" % (
                    constants.END_LOCATION - constants.START_LOCATION,
                    counter
                )
                counter += 1
                time.sleep(1)
    finally:
        os.close(fd)
        os.unlink(constants.BACKUP_FILE)


if __name__ == "__main__":
    main()
