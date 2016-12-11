# Util models for all EX05
import errno
import fcntl
import os
import select
import socket

from disconnect import Disconnect

BASIC_SELECT = select.POLLERR | select.POLLHUP


def add_to_database(database, s, peer):
    database[socket.fileno()] = {
        "socket": s,
        "buff": "",
        "peer": peer.fileno()
    }
    return database


def set_non_blocking(Fd):
    fcntl.fcntl(
        Fd,
        fcntl.F_SETFL, fcntl.fcntl(Fd, fcntl.F_GETFL) | os.O_NONBLOCK
    )


def build_poller(database, limit):
    poller = select.poll()
    events = BASIC_SELECT
    for fd in database:
        buff = database[fd]["buff"]
        if buff:
            events = events | select.POLLOUT
            if len(buff) < limit:
                events = events | select.POLLIN
        else:
            events = events | select.POLLIN
        poller.register(database[fd]["socket"], events)
    return poller


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
    while buff:
        try:
            buff = buff[s.send(buff):]
        except socket.error as e:
            if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
