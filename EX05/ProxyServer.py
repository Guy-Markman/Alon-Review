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
        bind_address,
        connect_address
    ):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(bind_address)
        s.setblocking(0)
        s.listen(1)
        self._add_to_database(
            s, None, "proxy", connect_address)  # TODO: peer None

    def _add_socket(self, bind_address, bind_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)
        s.bind((bind_address, bind_port))
        return s

    def _add_to_database(
        self,
        s,
        peer,
        state,
        address=None
    ):
        self._database[s.fileno()] = {
            "socket": s,  # our socket
            "buff": "",  # Buff to send to socket
            "peer": peer.fileno(),  # Peer in database
            "state": state,  # Proxy, active or close # TODO: Merge type and open connection
            "connect_address": address,  # For proxy only, where to connect
        }

    def _close_fd(self, entry):
        if entry["peer"] in self._database.keys():  # TODO: keys and peer
            peer_database = self._database[entry["peer"]]
            peer_database["peer"] = None
            peer_database["state"] = "close"
        entry["socket"].close()
        self._database.pop(fd)

    def _close_all_connections(self):
        for fd in self._database:
            self._database[fd]["state"] = "close"

    # TODO Entry instead of fd  and exception
    def _connect_both_sides(self, entry, args):
        try:
            accepted, addr = entry["socket"].accept()
            connection = "active"
            accepted.setblocking(0)
            active = self._add_socket(
                args.our_address, args.bind_port_active)
            try:
                active.connect(entry["connect_address"])
            except socket.error as e:
                if e.errno != errno.EINPROGRESS:
                    connection = False

            self._add_to_database(accepted, active, state=connection)
            self._add_to_database(active, accepted, state=connection)
        except Exception as e:
            if accepted in locals():
                accepted.close()
                fd_accepted = accepted.fileno()
                if fd_accepted in self._database.keys():
                    self._database.pop(fd_accepted)

            if active in locals():
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
            elif entry["peer"] is not None and entry["state"] != "close":
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
                        self._close_fd(entry)
                if not self.run:
                    self._close_all_connections()
                poller = self._build_poller()
                for fd, flag in poller.poll():
                    print "fd: %s and Events %s" % (fd, flag)
                    entry = self._database[fd]
                    if flag & select.POLLIN:
                        if entry["state"] == "close":
                            self._connect_both_sides(  # TODO: never pass
                                fd, args)
                        else:
                            data = ""
                            try:
                                data = self.recv(entry)
                                self._database[entry["peer"]]["buff"] += data
                            except disconnect.Disconnect:  # TODO: any other exception
                                entry["state"] = "close"
                            except Exception:
                                if data != "":
                                    if entry["peer"] is not None:
                                        self._database[entry["peer"]][
                                            "buff"] += data

                    if flag & (
                            select.POLLHUP | select.POLLERR):  # TODO: close socket
                        self._close_fd(entry)

                    if flag & select.POLLOUT:
                        left = 0
                        try:
                            left = self.send(  # Move send and recv to here TODO
                                entry)
                            entry["buff"] = entry["buff"][left:]
                        except Exception as e:
                            if left != 0:
                                entry["buff"] = entry["buff"][left:]
            except BaseException as e:
                self.close_all_connections()  # TODO: EINTER AND CTRL C
                exce = e
        if exce:
            raise exce

    def recv(self, entry):
        limit = self.buff_size
        ret = ""
        entry_socket = entry["socket"]
        while len(ret) < self.buff_size:
            try:
                buff = entry_buff.recv(limit - len(ret))
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

    def send(self, entry):
        entry_buff = entry["buff"]
        start = len(entry_buff)
        while entry_buff:
            try:
                entry_buff = entry_buff[entry["socket"].send(entry_buff):]
            except socket.error as e:
                if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
        return start - len(buff)
