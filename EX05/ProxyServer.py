#!/usr/bin/env python
# The proxy server we will creat
import errno
import select
import socket
import sys

import disconnect
import util


class ProxyServer(object):

    def __init__(self,
                 buffsize,
                 bind_port_passive,
                 bind_port_active,
                 port_passive
                 ):
        self.buff_size = buffsize
        self.connection_list = []
        self.database = {}
        self.current_bind_port_passive = bind_port_passive
        self.current_bind_port_active = bind_port_active
        self.current_port_passive = port_passive

    def add_proxy(self, bind_address, bind_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((bind_address, bind_port))
        s.setblocking(0)
        s.listen(1)
        self.connection_list.append(s)
        return s

    def terminate_handler(self, signum, frame):
        self.close_all_connections()
        sys.exit()

    def add_socket(self, bind_address, bind_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)
        s.bind((bind_address, bind_port))
        self.connection_list.append(s)
        return s

    def add_to_database(self, s, peer, connection_type):
        self.database[s.fileno()] = {
            "socket": s,
            "buff": "",
            "peer": peer.fileno(),
            "type": connection_type
        }

    def close_fd(self, fd):
        fd_database = self.database[fd]
        peer_database = self.database[fd_database["peer"]]
        self.connection_list.pop(
            self.connect_list.index(
                fd_database["socket"]))
        fd_database["socket"].close()
        self.database.pop(fd)
        self.connection_list.pop(
            self.connect_list.index(
                peer_database["socket"]))
        peer_database["socket"].close()
        self.database.pop(fd_database["peer"])

    def close_all_connections(self):
        for s in self.connection_list:
            s.close()

    def connect(self, fd, args):
        accepted, addr = self.database[fd]["socket"].accept()
        accepted.setblocking(0)
        self.connection_list.append(accepted)
        active = self.add_socket(
            args.our_address, 0)
        try:
            active.connect(
                (args.address_passive, self.current_port_passive))
        except socket.error as e:
            if e.errno != errno.EINPROGRESS:
                raise
        self.current_port_passive += 1
        self.add_to_database(accepted, active, "listen")
        self.add_to_database(active, accepted, "active")
        passive = self.add_proxy(
            args.our_address, self.current_bind_port_passive)
        self.add_to_database(passive, passive, "proxy")
        self.current_bind_port_passive += 1

    def proxy(self, args):
        try:
            passive = self.add_proxy(
                args.our_address, self.current_bind_port_passive)
            self.add_to_database(passive, passive, "proxy")
            self.current_bind_port_passive += 1
            while self.database:
                poller = util.build_poller(self.database, self.buff_size)
                events = poller.poll()
                for fd, flag in events:
                    if flag & select.POLLIN:
                        if self.database[fd]["type"] == "proxy":
                            self.connect(fd, args)
                            self.database.pop(fd)
                        else:
                            try:
                                data = util.recv(
                                    self.database[fd]["socket"], self.buff_size
                                )
                                if data:
                                    self.database[
                                        self.database[fd]["peer"]]["buff"] += \
                                        data
                                else:
                                    self.close_fd(fd)
                            except disconnect.Disconnect:
                                self.close_fd(fd)
                    if flag & (select.POLLHUP | select.POLLERR):
                        self.close_fd(fd)
                    if flag & select.POLLOUT:
                        util.send(
                            self.database[fd]["socket"],
                            self.database[fd]["buff"])
                        self.database[fd]["buff"] = ""
            self.close_all_connections()
        except:
            self.close_all_connections()
            raise
