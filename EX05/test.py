#!/usr/bin/python
import contextlib
import socket
import select

<<<<<<< HEAD

def main():
    with contextlib.closing(
        socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
    ) as s:
        s.bind(('127.0.0.1', 0))
        s.connect(('127.0.0.1', 8080))
        poller = select.poll()
        GOTDATA = select.POLLOUT | select.POLLERR | select.POLLHUP
        poller.register(s, GOTDATA)
        fd_to_socket = {s.fileno(): s,
                        }
        line = ""
        while True:
            for fd, event in poller.poll():
                print "(%s,%s)" % (fd, event)


def send(s, buffer):
    try:
        while buffer:
            buffer = buffer[s.send(buffer):]
    except OSError as e:
        if e.errno not in (errno.EWOULDBLOCK,
                           errno.EAGAIN
                           ):
            raise
=======
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
                    
>>>>>>> origin/dev

if __name__ == "__main__":
    main()
