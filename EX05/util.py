# Util models for all EX05
import errno
import fcntl
import os
import socket

from disconnect import Disconnect


def set_non_blocking(Fd):
    fcntl.fcntl(
        Fd,
        fcntl.F_SETFL, fcntl.fcntl(Fd, fcntl.F_GETFL) | os.O_NONBLOCK
    )


def recv(s, limit):
    print "start recving"
    ret = ""
    while len(ret) < limit:
        print "unlimited"
        try:
            print "stuck here?"
            buff = s.recv(limit - len(ret))
            print "nope"
            print buff
            if not buff:
                if not ret:
                    raise Disconnect()
                break
            ret += buff
        except socket.error as e:
            if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
            else:
                break
    return ret


def send(s, buff):
    start = len(buff)
    while buff:
        try:
            buff = buff[s.send(buff):]
        except socket.error as e:
            if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
    return start - len(buff)
