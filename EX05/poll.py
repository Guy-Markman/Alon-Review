# poll
import os
import socket
import sys
import select
import contextlib
import argparse
import ProxyServer

def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--Address-first", "-al",
        default = "127.0.0.1",
        type = str,
        help = "The address of the first program"
    )
    
    parser.add_argument(
        "--Port-first", "-pl",
        default = 8081,
        type = int,
        help = "The port of the first program"       
    )
    
    parser.add_argument(
        "--Address-second", "-al",
        default = "127.0.0.2",
        type = str,
        help = "The address of the second program"
    )
    
    parser.add_argument(
        "--Port-second", "-pl",
        default = 8082,
        type = int,
        help = "The port of the second program"       
    )
    
    parser.add_argument(
        "--Our-address", "-oa",
        default = "127.0.0.3",
        type = str,
        help = "Proxy Address"        
    )
    
    parse.add_argument(
        "--Our-port", "-op",
        default = 8080
    )
    return parser.parse_args()


def main():
    args = parse_args()
    server = ProxyServer()

if __name__ == "__main__":
    main()