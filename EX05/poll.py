#!/usr/bin/env python
# poll
import argparse

import ProxyServer


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--address-passive", "-ap",
        default="localhost",
        type=str,
        help="The address of the passive program"
    )

    parser.add_argument(
        "--port-passive", "-pp",
        default=8081,
        type=int,
        help="The port of the passive program"
    )

    parser.add_argument(
        "--bind-port-passive", "-bpp",
        default=8080,
        type=int,
        help="The port that our passive side will connect with"
    )

    parser.add_argument(
        "--bind-port-active", "-bpa",
        default=0,
        type=int,
        help="The port that our active side will bind to"
    )

    parser.add_argument(
        "--our-address", "-oa",
        default="localhost",
        type=str,
        help="Proxy Address"
    )

    parser.add_argument(
        "--buff", "-bf",
        default=1024,
        type=int,
        help="Buff size for each time"
    )

    return parser.parse_args()


def main():
    args = parse_args()
    b = args.buff
    server = ProxyServer.ProxyServer(b)

    server.proxy(args)


if __name__ == "__main__":
    main()
