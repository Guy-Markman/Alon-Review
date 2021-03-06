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
        nargs='+',
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
        address_list.append({
            "our address": (a[0], int(a[1])),
            "connect address": (a[2], int(a[3]))
        })
    parser.proxy = address_list
    return parser


def main():
    args = parse_args()
    server = ProxyServer.ProxyServer(args.buff_size)

    def terminate_handler(signo, frame):
        server.terminate()

    signal.signal(signal.SIGINT, terminate_handler)
    signal.signal(signal.SIGTERM, terminate_handler)
    for address_dict in args.proxy:
        server.add_proxy(
            address_dict["our address"],
            address_dict["connect address"]
        )
    server.proxy(args)


if __name__ == "__main__":
    main()
