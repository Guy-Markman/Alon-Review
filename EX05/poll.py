# poll
import argparse
import ProxyServer


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--passive-address", "-pa",
        default="127.0.0.1",
        type=str,
        help="The address of the passive program"
    )

    parser.add_argument(
        "--passive-port", "-pap",
        default=8080,
        type=int,
        help="The port of the passive program"
    )

    parser.add_argument(
        "--port-passive", "-pop",
        default=8081,
        type=int,
        help="The port of the passive program"
    )

    parser.add_argument(
        "--port-active", "-pa",
        default=0,
        type=int,
        help="The port that our active side will connect with"
    )

    parser.add_argument(
        "--port-address", "-oa",
        default="127.0.0.3",
        type=str,
        help="Proxy Address"
    )

    return parser.parse_args()


def main():
    args = parse_args()
    server = ProxyServer(args.Our_address, args.Port_active, args.Port_passive)
    server.proxy(args)

if __name__ == "__main__":
    main()
