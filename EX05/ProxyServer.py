#!/usr/bin/env python
# The proxy server we will creat
import socket
import select
import util
READ_WRITE = select.POLLIN | select.POLLHUP | select.POLLERR | select.POLLOUT
BUFF_SIZE = 1024


class ProxyServer(object):

    def __init__(self):
        self.connection_list = []

        self.active = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.passive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.database = {}
        self.add_to_database(self.passive, self.active)
        self.add_to_database(self.active, self.passive)

    def add_to_database(self, s, peer):
        self.database[socket.fileno()] = {
            "socket": s,
            "buff": "",
            "peer": peer.fileno()
        }

    def proxy(self, args):
        self.passive.bind((args.host, args.bind_passive))
        self.passive.listen(1)
        self.passive.setblocking(0)
        self.connection_list.append(self.passive)
        while True:
            poller = util.build_poller(self.database, BUFF_SIZE)
            for fd, flag in poller.poll():
                if flag & select.POOLIN:
                    if self.database[fd]["socket"] is self.passive:
                            s, address = self.database[fd]["socket"].accpet()
                            s.setblocking(0)
                            database = util.add_to_database(
                                self.database,
                                s,
                                self.active
                            )
                            database[self.active.fileno()]["peer"] = s.fileno()
                            self.connection_list.append(s)

                            self.active.bind((args.host, args.bind_active))
                            self.passive.setblocking(0)
                            self.connection_list.append(self.passive)
                    else:
                        data = util.recv(database[fd]["socket"], BUFF_SIZE)
                        if data:
                            database[database[fd]["peer"]]["buff"] += data
                            poller.modify(s, READ_WRITE)

                        else:
                            self.connection_list.pop(s)
                            s.close()
                if flag & (select.POLLHUP | select.POLLERR):
                    self.connection_list.pop(s)
                    s.close()
                if flag & select.POLLOUT & database[fd]["buff"]:
                    util.send(database[fd]["socket"], database[fd]["buff"])
