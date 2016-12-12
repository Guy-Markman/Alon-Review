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
    ret = ""
    while len(ret) < limit:
        try:
            buff = s.recv(limit - len(ret))
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
