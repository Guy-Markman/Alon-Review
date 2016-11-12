#!/usr/bin/env python
# poll
import argparse
import ProxyServer


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--address-passive", "-ap",
        default="127.0.0.1",
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
        "--port-passive", "-pop",
        default=8081,
        type=int,
        help="The port that our active side will connect with"
    )

    # TODO: Add aguments whice we will port bind it to self.active

    parser.add_argument(
        "--our-address", "-oa",
        default="127.0.0.3",
        type=str,
        help="Proxy Address"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    #TODO: Assign right args
    server = ProxyServer(
        args.Our_address,
        args.Port_active,
        args.Port_passive
    )

    server.proxy()

if __name__ == "__main__":
    main()
