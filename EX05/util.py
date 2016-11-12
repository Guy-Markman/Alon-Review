# Util models for all EX05
import fcntl
import socket
import os


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
