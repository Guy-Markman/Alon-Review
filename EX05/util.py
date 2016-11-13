# Util models for all EX05
import fcntl
import socket
import os
import errno
from disconnect import Disconnect
import select

BASIC_SELECT = select.POLLERR | select.POLLOUT


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
    for fd in database:
        if database[fd]["buff"]:
            if len(database[fd]["buff"]) < limit:
                poller.register(
                    database[fd]["socket"],
                    BASIC_SELECT | select.POLLIN | select.POLLOUT)
            else:
                poller.register(
                    database[fd]["socket"],
                    BASIC_SELECT | select.POOLOUT
                )
        else:
            poller.register(
                database[fd]["socket"],
                BASIC_SELECT | select.POOLIN
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
        except os.ERRNO as e:
            if e.errno not in (errno.EWOULDBLOCK | errno.EAGAIN):
                raise
    return ret


def send(s, buff):
    try:
        while buff:
            buff = buff[s.send(buff):]
    except os.ERRNO as e:
        if e.errno not in (errno.EWOULDBLOCK | errno.EAGAIN):
            raise
