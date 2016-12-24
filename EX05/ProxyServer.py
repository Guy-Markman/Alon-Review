#!/usr/bin/env python
# The proxy server we will creat
import errno
import select
import socket

import disconnect

CLOSE, PROXY, ACTIVE = range(3)


class ProxyServer(object):
    _database = {}

    def __init__(
        self,
        buffsize,
    ):
        self.buff_size = buffsize
        self.run = True

    def terminate(self):
        self.run = False

    def add_proxy(
        self,
        address_dict
    ):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(address_dict["our address"])
        s.setblocking(0)
        s.listen(1)
        self._add_to_database(
            s,
            None,
            "proxy",
            address_dict["connect address"]
        )

    def _add_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)
        return s

    def _add_to_database(
        self,
        s,
        peer,
        state,
        address=None
    ):
        peer_fileno = None if peer is None else peer.fileno()
        self._database[s.fileno()] = {
            "socket": s,  # our socket
            "buff": "",  # Buff to send to socket
            "peer": peer_fileno,  # Peer in database
            "state": state,  # Proxy, active or close
            "connect_address": address,  # For proxy only, where to connect
        }

    def _close_fd(self, fd):
        entry = self._database[fd]
        entry_peer = entry["peer"]

        if entry_peer is not None:
            peer_database = self._database[entry["peer"]]
            peer_database.update({
                "peer": None,
                "state": "close"
            })
        entry["socket"].close()
        self._database.pop(fd)

    def _close_all_connections(self):
        for fd in self._database:
            self._database[fd]["state"] = "close"

    def _connect_both_sides(self, entry):
        socket_list = []
        try:
            accepted, addr = entry["socket"].accept()
            socket_list.append(accepted)
            connection = "active"
            accepted.setblocking(0)
            active = self._add_socket()
            socket_list.append(active)
            try:
                active.connect(entry["connect_address"])
            except socket.error as e:
                if e.errno != errno.EINPROGRESS:
                    connection = False

            self._add_to_database(accepted, active, state=connection)
            self._add_to_database(active, accepted, state=connection)
        except Exception as e:
            for s in socket_list:
                s.close()
                fd_socekt = s.fileno()
                if fd_socekt in self._database.keys():
                    self._database.pop(fd_socekt)

    def _build_poller(self):
        poller = select.poll()
        for fd in self._database:
            entry = self._database[fd]
            events = select.POLLERR
            if entry["buff"]:
                events |= select.POLLOUT
            if entry["state"]:
                fd_peer = entry["peer"]
                if (
                    fd_peer is not None and
                    len(self._database[fd_peer]) < self.buff_size
                ):
                    events |= select.POLLIN
            poller.register(entry["socket"], events)
        return poller

    def proxy(self, args):
        exce = None  # Exception to raise
        while self._database:
            try:
                if not self.run:
                    self._close_all_connections()
                poller = self._build_poller()
                events = ()
                try:
                    events = poller.poll()
                except select.error as e:
                    if e[0] != errno.EINTR:
                        raise
                for fd, flag in events:
                    entry = self._database[fd]
                    if flag & select.POLLIN:
                        if entry["state"] == PROXY:
                            self._connect_both_sides(entry)
                        else:
                            self.recv(fd)

                    if flag & (select.POLLHUP | select.POLLERR):
                        raise disconnect.Disconnect()

                    if flag & select.POLLOUT:
                        try:
                            while True:
                                self.send(entry)
                        except socket.error as e:
                            if e.errno not in(errno.EWOULDBLOCK, errno.EAGAIN):
                                raise

                    for fd in self._database.keys():
                        entry = self._database[fd]
                        if not entry["state"] and not entry["buff"]:
                            self._close_fd(fd)
            except disconnect.Disconnect as e:
                self._database[fd]["state"] = CLOSE
            except Exception as e:
                self._close_fd(fd)
                exce = e
        if exce:
            raise exce

    def recv(self, entry):
        limit = self.buff_size
        ret = ""
        entry_socket = entry["socket"]
        while len(ret) < self.buff_size:
            try:
                buff = entry_socket.recv(limit - len(ret))
                if not buff:
                    if not ret:
                        raise disconnect.Disconnect(entry.keys()[0])
                    break
                ret += buff
            except socket.error as e:
                if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
                break
            self._database[entry["peer"]]["buff"] += ret

    def send(self, entry):
        entry_buff = entry["buff"]
        start = len(entry_buff)
        while entry_buff:
            try:
                entry_buff = entry_buff[entry["socket"].send(entry_buff):]
            except socket.error as e:
                if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
        entry["buff"] = entry["buff"][start - len(entry_buff):]
