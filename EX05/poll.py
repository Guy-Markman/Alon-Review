#!/usr/bin/env python
# poll
import socket
import select
import argparse
import errno
from disconnect import Disconnect
import logging
TIMEOUT = 10000
READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
READ_WRITE = READ_ONLY | select.POLLOUT
LOG_PREFIX = 'my'
def setup_logging(stream=None, level=logging.INFO):
    logger = logging.getLogger(LOG_PREFIX)
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

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--our-address", "-oa",
        default="127.0.0.1",
        type=str,
        help="Proxy Address"
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
    
    parser.add_argument(
        "--bind-port-active",
        "-bpa",
        default=8083,
        type=int,
        help="""The port we will bind on our machine
            and active will connect to it"""
    )

    parser.add_argument(
        "--bind-port-passive", "-bpp",
        default=8081,
        type=int,
        help="""The port we will bind on our machine and will
            connect to passive with it"""
    )

    parser.add_argument(
        "--address-passive", "-ap",
        default="127.0.0.1",
        type=str,
        help="Address of passive"
    )

    parser.add_argument(
        "--port-passive", "-pp",
        default=8080,
        type=int,
        help="The port of passive we will connect with"
    )
    args =parser.parse_args()
    args.log_level = LOG_STR_LEVELS[args.log_level_str]
    return args


def send(s, buffer):
    try:
        while buffer:
            buffer = buffer[s.send(buffer):]
    except OSError as e:
        if e.errno not in (errno.EWOULDBLOCK,
                           errno.EAGAIN
                           ):
            raise


def recv(s, limit):
    try:
        ret = ""
        while len(ret) < limit:
            buf = s.recv(limit - len(ret))
            if not buf:
                raise Disconnect()
            ret += buf
    except OSError as e:
        if e.errno not in (errno.EWOULDBLOCK,
                           errno.EAGAIN
                           ):
            raise


def build_data(data, socket, peer, mode):
    data[socket.fileno()] = {
        "socket": socket,
        "buff": "",
        "peer": peer,
        "mode": mode
    }
    return data


def main():
    args = parse_args()
    
    if args.log_file:
        logger = setup_logging(
            stream=open(args.log_file, 'a'),
            level=args.log_level,
        )
    else:
        logger = setup_logging(
            level=args.log_level,
        )
    logger.debug("Start")
    passive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.debug("Connect to (%s,%s)" %(args. our_address,args.bind_port_passive ))
    passive.bind((args.our_address, args.bind_port_passive))
    passive.listen(1)

    active = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    active.bind((args.our_address, args.bind_port_active))

    poller = select.poll()
    
    database={}
    database = build_data(database, passive, active, "LISTEN")
    database = build_data(database, active, passive, "ACTIVE")
    
    poller.register(passive, READ_WRITE)
    
    logger.debug("Setup")
    
    logger.debug("active %s" %active.fileno())
    logger.debug("passive %s" % passive.fileno())
    logger.debug(select.POLLOUT)
    while True:
        for fd, flag in poller.poll(TIMEOUT):
            logger.debug("event (%s,%s)" %(fd, flag))
            s = database[fd]["socket"]
            if flag & select.POLLIN:
                if s is passive:
                    connection, add = s.accept()
                    connection.setblocking(0)
                    logger.debug((args.address_passive,args.port_passive))
                    active.connect((localhost,8080))
                    poller.register(active, READ_WRITE)
                    database = build_data(database, connection, active, "ACTIVE")
                    poller.register(connection, READ_ONLY)
            elif flag & select.POLLHUP:
                poller.unregister(s)
                s.close()
            elif flag & select.POLLOUT:
                if database[s.fileno()]["buff"]:
                    send(s, database[s.fileno()]["buff"])
            
            elif flag & select.POLLERR:
                poller.debug("Yes")
                poller.unregister(s)
                s.close()


if __name__ == "__main__":
    main()
