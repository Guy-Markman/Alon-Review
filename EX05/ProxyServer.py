#!/usr/bin/env python
# The proxy server we will creat
import errno
import select
import socket

import disconnect

BASIC_SELECT = select.POLLERR | select.POLLHUP


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
        address_list
    ):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(address_list[0])
        s.setblocking(0)
        s.listen(1)
        self._add_to_database(
            s, None, "proxy", address_list[1]
        )

    def _add_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)  # TODO: Check with alon if bind is must
        return s

    def _add_to_database(
        self,
        s,
        peer,
        state,
        address=None
    ):
        if peer is not None:
            peer_fileno = peer.fileno()
        else:
            peer_fileno = None
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
            peer_database["peer"] = None
            peer_database["state"] = "close"
        entry["socket"].close()
        self._database.pop(fd)

    def _close_all_connections(self):
        for fd in self._database:
            self._database[fd]["state"] = "close"

    def _connect_both_sides(self, entry):
        try:
            accepted, addr = entry["socket"].accept()
            connection = "active"
            accepted.setblocking(0)
            active = self._add_socket()
            try:
                active.connect(entry["connect_address"])
            except socket.error as e:
                if e.errno != errno.EINPROGRESS:
                    connection = False

            self._add_to_database(accepted, active, state=connection)
            self._add_to_database(active, accepted, state=connection)
        except Exception as e:
            if 'accepted' in locals():
                accepted.close()
                fd_accepted = accepted.fileno()
                if fd_accepted in self._database.keys():
                    self._database.pop(fd_accepted)

            if 'active' in locals():
                active.close()
                fd_active = active.fileno()
                if fd_active in self._database.keys():
                    self._database.pop(fd_active)

    def _build_poller(self):
        poller = select.poll()
        for fd in self._database:
            entry = self._database[fd]
            events = BASIC_SELECT
            buff = entry["buff"]
            if buff:
                events |= select.POLLOUT
                fd_peer = entry["peer"]
                if fd_peer is not None:
                    peer_buff = self._database[fd_peer]["buff"]
                    if len(peer_buff) < self.buff_size and \
                            entry["state"] != "close":
                        events |= select.POLLIN
            elif (entry["peer"] is not None or entry["state"] == "proxy") and \
                    entry["state"] != "close":
                events |= select.POLLIN
            poller.register(entry["socket"], events)
        return poller

    def proxy(self, args):
        exce = None  # Exception to raise
        while self._database:
            try:
                if not self.run:
                    self._close_all_connections()
                for fd in self._database.keys():
                    entry = self._database[fd]
                    if entry["state"] == "close" and not entry["buff"]:
                        self._close_fd(fd)

                if not self._database:
                    break

                poller = self._build_poller()
                try:
                    events = poller.poll()
                except select.error as e:
                    if e[0] != errno.EINTR:
                        raise
                    events = ()
                for fd, flag in events:
                    entry = self._database[fd]
                    if flag & select.POLLIN:
                        if entry["state"] == "proxy":
                            self._connect_both_sides(  # TODO: never pass
                                entry)

                        else:
                            data = ""
                            try:
                                data = self.recv(entry)
                                self._database[entry["peer"]]["buff"] += data
                            except disconnect.Disconnect:
                                entry["state"] = "close"
                            except Exception:
                                if data != "":
                                    self._database[entry["peer"]][
                                        "buff"] += data

                    if flag & (
                            select.POLLHUP | select.POLLERR):
                        self._close_fd(fd)

                    if flag & select.POLLOUT:
                        left = 0
                        try:
                            left = self.send(
                                entry)
                            entry["buff"] = entry["buff"][left:]
                        except Exception as e:
                            if left != 0:
                                entry["buff"] = entry["buff"][left:]
            except Exception as e:
                self._close_all_connections()  # TODO: EINTER AND CTRL C
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
                        raise disconnect.Disconnect()
                    break
                ret += buff
            except socket.error as e:
                if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
                else:
                    break
        return ret

    def send(self, entry):
        entry_buff = entry["buff"]
        start = len(entry_buff)
        while entry_buff:
            try:
                entry_buff = entry_buff[entry["socket"].send(entry_buff):]
            except socket.error as e:
                if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
        return start - len(entry_buff)
