#!/usr/bin/env python
# poll
import argparse
import signal

import ProxyServer


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--our-address",
        default="localhost:8080",
        help="Our address, default %(default)d",
    )

    parser.add_argument(
        "--connect-address",
        default=["localhost:8061"],
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
    parser.our_address = (parser.our_address[0], int(parser.our_address[1]))
    address_list = []
    for address in parser.connect_address:
        address_list.append([address[0], int(address[1])])
    return parser.parse_args()


def main():
    args = parse_args()
    server = ProxyServer.ProxyServer(args.buff_size)
    def xxx(signo, frame):
        server.terminate()

    signal.signal(signal.SIGINT, xxx)
    signal.signal(signal.SIGTERM, xxx)
    server.add_proxy(
        args.our_address,  # TODO: address:port:connect:portconnect
        args.bind_port_passive,
        args.connect_address,
        args.connect_port
    )
    server.proxy(args)


if __name__ == "__main__":
    main()
