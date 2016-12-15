#!/usr/bin/env python
# poll
import argparse

import ProxyServer


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--address-passive", "-ap",
        default="localhost",
        help="The address of the passive program,default  %(default)s"
    )

    parser.add_argument(
        "--connect-address",
        default="localhost",
        help="The address of the passive program, default %(default)s"
    )

    parser.add_argument(
        "--connect-port", "-pp",
        default=8061,
        type=int,
        help="The port of the passive program, default %(default)d"
    )

    parser.add_argument(
        "--bind-port-passive",
        "-bpp",
        default=8080,
        type=int,
        help='''The port that our passive side will connect with, default
            %(default)d'''
    )

    parser.add_argument(
        "--bind-port-active", "-bpa",
        default=0,
        type=int,
        help="The port that our active side will bind to, default %(default)d"
    )

    parser.add_argument(
        "--our-address", "-oa",
        default="localhost",
        help="Proxy Address, default %(default)s"
    )

    parser.add_argument(
        "--buff-size", "-bf",
        default=1024,
        type=int,
        help="Buff size for each time, default %(default)d"
    )

    return parser.parse_args()


def main():
    args = parse_args()
    server = ProxyServer.ProxyServer(
        args.buff_size,
    )
    server.add_proxy("localhost", 8081, "localhost", 8080)
    server.add_proxy("localhost", 8082, "localhost", 8081)
    server.add_proxy("localhost", 8083, "localhost", 8082)
    server.proxy(args)


if __name__ == "__main__":
    main()
