#!/usr/bin/env python
# The proxy server we will creat
import errno
import select
import socket

import disconnect
import util

BASIC_SELECT = select.POLLERR | select.POLLHUP


class ProxyServer(object):
    _database = {}
    _socket_fd = {}

    def __init__(
        self,
        buffsize,
    ):
        self.buff_size = buffsize

    def add_proxy(
            self,
            bind_address,
            bind_port,
            connect_address,
            connect_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((bind_address, bind_port))
        s.setblocking(0)
        s.listen(1)
        self._add_to_database(s, s, "proxy", connect_address, connect_port)
        self._socket_fd[s] = s.filno()

    def _add_socket(self, bind_address, bind_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)
        s.bind((bind_address, bind_port))
        self._socket_fd[s] = s.fileno()
        return s

    def _add_to_database(
        self,
        s,
        peer,
        connection_type,
        connect_address=None,
        connect_port=None,
        open_connection=True,
    ):
        self._database[s.fileno()] = {
            "socket": s,  # our socket
            "buff": "",  # Buff to send to socket
            "peer": peer.fileno(),  # Peer in database
            "type": connection_type,  # Proxy or active
            "connect_address": connect_address,  # For proxy only, where to
            "connect_port": connect_port,  # Connect when someone connect to it
            "open_connection": True  # Able to get/recv data
        }

    def _close_fd(self, fd):
        fd_database = self._database[fd]
        try:
            self._database[fd_database["peer"]]["open_connection"] = False
        except KeyError:  # Whice mean the peer already removed
            pass
        self.socket_fd.pop(fd_database["socket"])
        fd_database["socket"].close()
        self._database.pop(fd)

    def _close_all_connections(self):
        for fd in self._database:
            self._database[fd]["open_connection"] = False

    def _connect_both_sides(self, fd, args):
        accepted, addr = self._database[fd]["socket"].accept()
        connection = True
        accepted.setblocking(0)
        active = self._add_socket(
            args.our_address, args.bind_port_active)
        try:
            active.connect(
                (self._database[fd]["connect_address"],
                 self._database[fd]["connect_port"]))
        except socket.error as e:
            if e.errno != errno.EINPROGRESS:
                connection = False
        self._socket_fd[accepted] = accepted.fileno()
        self._add_to_database(accepted, active, "active",
                              open_connection=connection)
        self._socket_fd[active] = active.fileno()
        self._add_to_database(active, accepted, "active",
                              open_connection=connection)

    def _build_poller(self):
        poller = select.poll()
        for fd in self._database:
            entry = self._database[fd]
            events = BASIC_SELECT
            buff = entry["buff"]
            if buff:
                events |= select.POLLOUT
                peer_buff = self._database[entry["peer"]]["buff"]
                if len(peer_buff) < self.buff_size and \
                        entry["open_connection"]:
                    events |= select.POLLIN
            elif entry["open_connection"]:
                events |= select.POLLIN
            poller.register(entry["socket"], events)

        return poller

    def _build_select(self):
        rlist = []
        wlist = []
        keys = self._database.keys()
        xlist = []
        socket_fd = {}
        for fd in self._database:
            entry = self._database[fd]
            entry_socket = entry["socket"]
            xlist.append(entry_socket)
            socket_fd[entry_socket] = fd
            buff = entry["buff"]
            if buff:
                wlist.append(entry_socket)
                entry_peer = entry["peer"]
                if entry_peer in keys:
                    peer_buff = self._database[entry_peer]["buff"]
                    if len(peer_buff) < self.buff_size and \
                            entry["open_connection"]:
                        rlist.append(entry_socket)
            elif entry["open_connection"]:
                rlist.append(entry_socket)
        return (rlist, wlist, xlist)

    def proxySelect(self, args):
        exce = None  # Exception to raise
        while True:
            try:
                for fd in self._database.keys():
                    entry = self._database[fd]
                    if not entry["open_connection"] and not entry["buff"]:
                        self._close_fd(fd)
                if not self._database:
                    break
                rlist, wlist, xlist = self._build_select()
                rlist, wlist, xlist = select.select(rlist, wlist, xlist)

                for s in rlist:
                    entry = self._database[self._socket_fd[s]]
                    if entry["type"] == "proxy":
                        try:
                            self._connect_both_sides(
                                fd, args)
                        except socket.error:
                            pass
                    else:
                        try:
                            data = util.recv(
                                entry["socket"],
                                self.buff_size -
                                len(self._database[entry["peer"]]["buff"])
                            )
                            self._database[
                                entry["peer"]]["buff"] +=\
                                data
                        except disconnect.Disconnect:
                            entry["open_connection"] = False
                for s in xlist:
                    self._database[self._socket_fd[s]][
                        "open_connection"] = False
                for s in wlist:
                    entry = self._database[self._socket_fd[s]]
            except BaseException as e:
                self._close_all_connections()
                exce = e
        if exce:
            raise exce

    def proxyPoll(self, args):
        exce = None  # Exception to raise
        while True:
            try:
                for fd in self._database.keys():
                    entry = self._database[fd]
                    if not entry["open_connection"] and not entry["buff"]:
                        self._close_fd(fd)
                if not self._database:
                    break
                poller = self._build_poller()
                events = poller.poll()
                for fd, flag in events:
                    entry = self._database[fd]
                    if flag & select.POLLIN:
                        if entry["type"] == "proxy":
                            try:
                                self._connect_both_sides(
                                    fd, args)
                            except socket.error:
                                pass
                        else:
                            try:
                                data = util.recv(
                                    entry["socket"],
                                    self.buff_size -
                                    len(self._database[entry["peer"]]["buff"])
                                )

                                self._database[
                                    entry["peer"]]["buff"] +=\
                                    data
                            except disconnect.Disconnect:
                                entry["open_connection"] = False
                    if flag & (select.POLLHUP | select.POLLERR):
                        entry["open_connection"] = False

                    if flag & select.POLLOUT:
                        left = util.send(
                            entry["socket"],
                            entry["buff"])
                        entry["buff"] = entry["buff"][left:]
            except BaseException as e:
                self._close_all_connections()
                exce = e
        if exce:
            raise exce
