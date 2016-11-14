#!/usr/bin/env python
import constants
import contextlib
import mmap
import os
import stat
import time


def main():
    fd = os.open(
        constants.BACKUP_FILE,
        os.O_CREAT | os.O_RDWR,
        stat.S_IREAD | stat.S_IWRITE | stat.S_IRGRP | stat.S_IROTH
    )

    os.lseek(fd, constants.FILE_SIZE, os.SEEK_SET)
    os.write(fd, "\0")
    try:
        with contextlib.closing(mmap.mmap(fd, 1024)) as mm:
            counter = 0
            while True:
                mm[
                    constants.START_LOCATION:
                    constants.END_LOCATION
                ] = "%4x" % counter
                counter += 1
                time.sleep(1)
    finally:
        os.close(fd)
        os.unlink(constants.BACKUP_FILE)


if __name__ == "__main__":
    main()
