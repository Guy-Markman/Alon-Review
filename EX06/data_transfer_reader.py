#!/usr/bin/env python
import argparse
import contextlib
import logging
import mmap
import os
import stat

import base
import constants
import CyclicBuffer
import util

NUMER_OF_BYTES_FOR_TEST = 21474836480  # 20GB
EMPTY = "\0"


def parse_args():
    parser = argparse.ArgumentParser(
        prog="package name",
        description=("package"),
    )

    parser.add_argument(
        "--test-bytes", "-tb",
        default=NUMER_OF_BYTES_FOR_TEST,
        help="Number of bytes for the test, defualt 20GB",
        type=int
    )
    LOG_STR_LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    parser.add_argument(
        '--log-level',
        dest='log_level_str',
        default='INFO',
        choices=LOG_STR_LEVELS.keys(),
        help='Log level',
    )
    parser.add_argument(
        '--log-file',
        dest='log_file',
        metavar='FILE',
        required=False,
        help='Logfile to write to, otherwise will log to console.',
    )
    args = parser.parse_args()
    args.log_level = LOG_STR_LEVELS[args.log_level_str]
    return args


def main():
    args = parse_args()
    if args.log_file:
        logger = base.setup_logging(
            stream=open(args.log_file, 'a'),
            level=args.log_level,
        )
    else:
        logger = base.setup_logging(
            level=args.log_level,
        )
    fd = os.open(
        constants.BACKUP_FILE,
        os.O_RDWR,
        stat.S_IREAD | stat.S_IWRITE | stat.S_IRGRP | stat.S_IROTH
    )
    while os.fstat(fd).st_size < constants.FILE_SIZE:
        os.lseek(fd, constants.FILE_SIZE - 1, os.SEEK_SET)
        os.write(fd, EMPTY)
    try:
        with contextlib.closing(mmap.mmap(fd, constants.BUFFER_SIZE)) as mm:
            logger.debug("Started")
            cb = CyclicBuffer.CyclicBuffer(mm)
            logger.debug("Forked child")
            sum = 0
            for x in xrange(args.test_bytes):
                byte = cb.read_head()
                sum += util.bin_to_int(byte)
            util.write_to_target(1, "reader %d" % sum)
    finally:
        os.close(fd)


if __name__ == "__main__":
    main()
