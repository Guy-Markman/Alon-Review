import logging

"""
To Init:

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

"""


class Base(object):
    """Base of all objects"""

    LOG_PREFIX = 'my'

    @property
    def logger(self):
        """Logger."""
        return self._logger

    def __init__(self):
        """Contructor."""
        self._logger = logging.getLogger(
            '%s.%s' % (
                self.LOG_PREFIX,
                self.__module__,
            ),
        )


def setup_logging(stream=None, level=logging.INFO):
    logger = logging.getLogger(Base.LOG_PREFIX)
    logger.propagate = False
    logger.setLevel(level)

    try:
        h = logging.StreamHandler(stream)
        h.setLevel(level)
        h.setFormatter(logging.Formatter(
                    fmt=(
                        '%(asctime)-15s '
                        '[%(levelname)-7s] '
                        '%(name)s@%(process)d::%(funcName)s:%(lineno)d '
                        '%(message)s'
                    ),
                ),)
        logger.addHandler(h)

    except IOError:
        logging.warning('Cannot initialize logging', exc_info=True)

    return logger
