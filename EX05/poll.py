#!/usr/bin/env python
# poll
import argparse
import signal

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
        default=8061,
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
    server = ProxyServer.ProxyServer(
        args.buff,
        args.bind_port_passive,
        args.bind_port_active,
        args.port_passive
    )
    # I prefer to kill it (the best way to close the program) without exception
    signal.signal(signal.SIGINT, server.terminate_handler)
    signal.signal(signal.SIGTERM, server.terminate_handler)
    server.proxy(args)


if __name__ == "__main__":
    main()
