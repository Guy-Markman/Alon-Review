#!/usr/bin/env python
# The proxy server we will creat
import errno
import select
import socket
import sys
import disconnect
import util

BASIC_SELECT = select.POLLERR | select.POLLHUP


class ProxyServer(object):
    _database = {}

    def __init__(
        self,
        buffsize,
        port_passive,
    ):
        self.buff_size = buffsize
        self.current_port_passive = port_passive

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
        self.add_to_database(s, s, "proxy", connect_address, connect_port)

    # Used when CTRL-C or kill the program
    def terminate_handler(self, signum, frame):
        self.close_all_connections()
        sys.exit()

    def add_socket(self, bind_address, bind_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)
        s.bind((bind_address, bind_port))
        return s

    def add_to_database(
            self,
            s,
            peer,
            connection_type,
            connect_address=None,
            connect_port=None):
        self._database[s.fileno()] = {
            "socket": s,
            "buff": "",
            "peer": peer.fileno(),
            "type": connection_type,
            "connect_address": connect_address,
            "connect_port": connect_port,
        }

    def close_fd(self, fd):
        fd_database = self._database[fd]
        peer_fd = fd_database["peer"]
        peer_database = self._database[peer_fd]
        fd_database["socket"].close()
        while peer_database["buff"]:
            left = util.send(
                peer_database["socket"],
                peer_database["buff"]
            )
            peer_database["buff"] = peer_database["buff"][left:]
        peer_database["socket"].close()

        self._database.pop(fd)
        self._database.pop(fd_database["peer"])

    def close_all_connections(self):  # remove connecntion_list
        for fd in self._database:
            self._database[fd]["socket"].close()

    def connect_both_sides(self, fd, args):  # change name"
        accepted, addr = self._database[fd]["socket"].accept()
        accepted.setblocking(0)
        active = self.add_socket(
            args.our_address, args.bind_port_active)
        try:
            active.connect(
                (self._database[fd]["connect_address"],
                 self._database[fd]["connect_port"]))
        except socket.error as e:
            if e.errno != errno.EINPROGRESS:  # not throwing everything, close handles
                accepted.close()
                raise

        self.add_to_database(accepted, active, "active")
        self.add_to_database(active, accepted, "active")

    def build_poller(self):  # move to proxy
        poller = select.poll()
        events = BASIC_SELECT
        for fd in self._database:
            buff = self._database[fd]["buff"]
            if buff:
                events |= select.POLLOUT  # |=
                if len(buff) < self.buff_size:  # change this
                    events |= select.POLLIN
            else:
                events |= select.POLLIN
            poller.register(self._database[fd]["socket"], events)
        return poller

    def proxy(self, args):
        try:
            while self._database:
                poller = self.build_poller()
                events = poller.poll()
                for fd, flag in events:
                    if flag & select.POLLIN:
                        if self._database[fd]["type"] == "proxy":
                            try:
                                self.connect_both_sides(
                                    fd, args)  # change name
                            except socket.error:
                                pass
                        else:
                            try:
                                data = util.recv(
                                    self._database[fd]["socket"],
                                    # not buffer size
                                    self.buff_size - \
                                    len(self._database[fd]["buff"])
                                )
                                if data is not None:
                                    self._database[
                                        self._database[fd]["peer"]]["buff"] +=\
                                        data
                                else:
                                    self.close_fd(fd)
                            except disconnect.Disconnect:
                                self.close_fd(fd)
                    if flag & (select.POLLHUP | select.POLLERR):
                        self.close_fd(fd)
                    if flag & select.POLLOUT:
                        left = util.send(  # return sent size
                            self._database[fd]["socket"],
                            self._database[fd]["buff"])
                        self._database[fd]["buff"] = self._database[
                            fd]["buff"][left:]
            self.close_all_connections()
        except:
            self.close_all_connections()
            raise
