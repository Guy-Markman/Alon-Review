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
        self.add_to_database(s, s, "proxy", connect_address, connect_port)

    # Used when CTRL-C or kill the program
    # class can't exit program
    # hanlder can't close
    def terminate_handler(self, signum, frame):
        self.close_all_connections()
        sys.exit()

    def _add_socket(self, bind_address, bind_port):
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
        while peer_database["buff"]: # can't send all here
            left = util.send(
                peer_database["socket"],
                peer_database["buff"]
            )
            peer_database["buff"] = peer_database["buff"][left:]
        peer_database["socket"].close()

        self._database.pop(fd)
        self._database.pop(fd_database["peer"])

    def close_all_connections(self):
        for fd in self._database:
            self._database[fd]["socket"].close()

    def connect_both_sides(self, fd, args):
        accepted, addr = self._database[fd]["socket"].accept()
        accepted.setblocking(0)
        active = self._add_socket(
            args.our_address, args.bind_port_active)
        try:
            active.connect(
                (self._database[fd]["connect_address"],
                 self._database[fd]["connect_port"]))
        except socket.error as e:
            if e.errno != errno.EINPROGRESS:
                accepted.close()
                raise
        finally: #how to clean it 
            

        self.add_to_database(accepted, active, "active")
        self.add_to_database(active, accepted, "active")

    def build_poller(self): # private all
        poller = select.poll()
        events = BASIC_SELECT
        for fd in self._database:
            buff = self._database[fd]["buff"]
            if buff:
                events |= select.POLLOUT
                if len(buff) < self.buff_size: # couple
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
                    entry = self._database[fd] # change it to everywhere
                    if flag & select.POLLIN:
                        if self._database[fd]["type"] == "proxy":
                            try:
                                self.connect_both_sides(
                                    fd, args)
                            except socket.error:
                                pass
                        else:
                            try:
                                data = util.recv(
                                    self._database[fd]["socket"],
                                    self.buff_size - \
                                    len(self._database[fd]["buff"])
                                )
                                if data:
                                    self._database[
                                        self._database[fd]["peer"]]["buff"] +=\
                                        data
                                else:
                                    self.close_fd(fd) # housekeeping in one location
                            except disconnect.Disconnect:
                                self.close_fd(fd)
                    if flag & (select.POLLHUP | select.POLLERR):
                        self.close_fd(fd)
                        
                    if flag & select.POLLOUT:
                        left = util.send(
                            self._database[fd]["socket"],
                            self._database[fd]["buff"])
                        self._database[fd]["buff"] = self._database[
                            fd]["buff"][left:]
        except:
            self.close_all_connections()
            raise
