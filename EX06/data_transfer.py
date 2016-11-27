#!/usr/bin/env python
import argparse
import contextlib
import logging
import mmap
import os
import time
import random

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


def proc_parent(cb, logger, returns):
    sum = 0
    for x in xrange(returns):
        num = random.randint(0, 255) #
        sum += num
        cb.write_head(util.int_to_bin(num))
        cb.increas_head()
    print sum


def proc_child(cb, logger, returns):
    sum = 0
    for x in xrange(returns):
        byte = cb.read_tail()
        sum += util.bin_to_int(byte)
        cb.increas_tail()
    print sum


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
    with contextlib.closing(mmap.mmap(-1, constants.BUFFER_SIZE)) as mm:
        logger.debug("Started")
        cb = CyclicBuffer.CyclicBuffer(mm)
        child = os.fork()
        if child == 0:
            logger.debug("Forked child")
            time.sleep(5)  # Let the parent write a little bit and then start
            proc_child(cb, logger, args.test_bytes)
        else:
            logger.debug("Forked parent")
            proc_parent(cb, logger, args.test_bytes)


if __name__ == "__main__":
    main()
