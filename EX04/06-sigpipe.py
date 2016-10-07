#!/usr/bin/env python
import util
import signal


def main():
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    while True:
        util.write_to_target(1, "hello\n")


if __name__ == "__main__":
    main()
'''The error I get is Broken Pipe
This is because even though I put it to sleep, the program still write.
The only thing that sleep is the OS.'''
