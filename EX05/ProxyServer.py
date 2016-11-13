#!/usr/bin/env python
# The proxy server we will creat
import socket
import select
import util
READ_WRITE = select.POLLIN | select.POLLHUP | select.POLLERR | select.POLLOUT
BUFF_SIZE = 1024


class ProxyServer(object):

    def __init__(self, host, bind_passive, bind_active):
        self.connection_list = []

        self.passive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.passive.bind((host, bind_passive))
        self.passive.listen(1)
        self.passive.setblocking(0)
        self.connection_list.append(self.passive)

        self.active = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active.bind((host, bind_active))
        self.passive.setblocking(0)
        self.connection_list.append(self.passive)

        self.poller = select.poll()

    def build_poller(self):
        self.poller = select.poll()
        for s in self.connection_list:
            self.poller.register(s, READ_WRITE)

    def proxy(self):
        database = util.add_to_database({}, self.passive, self.active)
        database = util.add_to_database(database, self.active, self.passive)
        while True:
            for fd, flag in self.poller.poll():
                if flag & select.POOLIN:
                    if database[fd]["socket"] is self.passive:
                            s, address = database[fd]["socket"].accpet()
                            s.setblocking(0)
                            database = util.add_to_database(
                                database,
                                s,
                                self.active
                            )
                            database[self.active.fileno()]["peer"] = s.fileno()
                            self.connection_list.append(s)
                    else:
                        data = util.recv(database[fd]["socket"], BUFF_SIZE)
                        if data:
                            database[database[fd]["peer"]]["buff"] += data
                            self.poller.modify(s, READ_WRITE)
                        else:
                            self.poller.unregister(s)
                            self.connection_list.pop(s)
                            s.close()
                if flag & (select.POLLHUP | select.POLLERR):
                    self.poller.unregister(s)
                    self.connection_list.pop(s)
                    s.close()
                if flag & select.POLLOUT & database[fd]["buff"]:
                    util.send(database[fd]["socket"], database[fd]["buff"])
