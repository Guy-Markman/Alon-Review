#!/usr/bin/env python
# poll
import argparse
import signal

import ProxyServer


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--proxy",
        default=["localhost:8080:localhost:8061"],
        nargs='?',
        help="The address(es) we will connect to, default %(default)d"
    )
    parser.add_argument(
        "--buff-size", "-bf",
        default=1024,
        type=int,
        help="Buff size for each time, default %(default)d"
    )
    parser = parser.parse_args()
    address_list = []
    for a in parser.proxy:
        a = a.split(":")
        if len(a) != 4:
            raise ValueError(
                """--proxy need to be in the next format:
                    proxy_address:proxy_port:remote_address:remote_port"""
            )
        address_list.append([(a[0], int(a[1])), (a[2], int(a[3]))])
    parser.proxy = address_list
    return parser


def main():
    args = parse_args()
    server = ProxyServer.ProxyServer(args.buff_size)

    def xxx(signo, frame):
        server.terminate()
    print args
    signal.signal(signal.SIGINT, xxx)
    signal.signal(signal.SIGTERM, xxx)
    for ad in args.proxy:
        server.add_proxy(ad)
    server.proxy(args)


if __name__ == "__main__":
    main()
