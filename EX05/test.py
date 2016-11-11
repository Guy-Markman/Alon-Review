#!/usr/bin/python
#cd /cygdrive/c/Users/Offer/Documents/GitHub/Alon-Review/EX05

import contextlib
import socket
import select

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
     fd_to_socket = { s.fileno(): s,
         }
     line = ""
     while True:
         for fd, event in poller.poll():
            print "(%s,%s)"%(fd,event)
                  
  
def send(s, buffer):
 try:
     while buffer:
         buffer = buffer[s.send(buffer):]
 except OSError as e:
     if e.errno not in (errno.EWOULDBLOCK,
                        errno.EAGAIN
                        ):
         raise
         
if __name__ == "__main__":
 main() 

