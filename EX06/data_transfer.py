#!/usr/bin/env python
import argparse
import contextlib
import logging
import mmap

import base
import constants
from CyclicBuffer import CyclicBuffer


def parse_args():
    parser = argparse.ArgumentParser(
        prog="package name",
        description=("package"),
    )

    parser.add_argument(
        "--buffer-name", "-bn",
        default=None,
        help="Buffer file name"
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
    logger = None

    if args.log_file:
        logger = base.setup_logging(
            stream=open(args.log_file, 'a'),
            level=args.log_level,
        )
    else:
        logger = base.setup_logging(
            level=args.log_level,
        )
    logger.debug("Args parsed")


def main():
    with contextlib.closing(mmap.mmap(-1, constants.BUFFER_SIZE)) as mm:
        cb = CyclicBuffer(mm)
        print type(cb.mm[-8:])


if __name__ == "__main__":
    main()
