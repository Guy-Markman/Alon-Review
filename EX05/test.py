#!/usr/bin/python
import contextlib
import socket
import select

with contextlib.closing(
    socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
    )
) as sl:
    sl.bind(('127.0.0.1', 8080))
    sl.listen(1)
    while True:
        s, addr = sl.accept()
        with contextlib.closing(s):
            poller = select.poll()
            GOTDATA = select.POLLIN | select.POLLERR | select.POLLHUP
            poller.register(s, GOTDATA)
            fd_to_socket = { s.fileno(): s,
                }
            line = ""
            while True:
                events = poller.poll()
                for fd, event in events:
                    data = s.recv(1000)
                    if len(data) == 0:
                        break
                    if data=="\r":
                        print line
                        line = ""
                    else:
                        line += data
                    

