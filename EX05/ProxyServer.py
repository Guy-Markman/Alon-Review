#!/usr/bin/env python
# The proxy server we will creat
import select
import socket
import errno
import disconnect
import util

READ_WRITE = select.POLLIN | select.POLLHUP | select.POLLERR | select.POLLOUT
BUFF_SIZE = 1024


class ProxyServer(object):

    def __init__(self, buffsize):
        self.buff_size = buffsize
        self.connection_list = []
        self.database = {}

    def add_proxy(self, bind_address, bind_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((bind_address, bind_port))
        s.setblocking(0)
        s.listen(1)
        self.connection_list.append(s)
        return s

  
    def add_socket(self, bind_address, bind_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)
        s.bind((bind_address, bind_port))
        self.connection_list.append(s)
        return s
        

    def add_to_database(self, s, peer):
        self.database[s.fileno()] = {
            "socket": s,
            "buff": "",
            "peer": peer.fileno()
        }

    def proxy(self, args):
        try:
            passive = self.add_proxy(args.our_address, args.bind_port_passive)
            poller = select.poll()
            poller.register(passive, select.POLLIN)
            while True:
                events = poller.poll()
                if events:
                    accepted, addr = passive.accept()
                    break
            active = self.add_socket(args.our_address, args.bind_port_active)
            try:
                active.connect((args.address_passive, args.port_passive))
            except socket.error as e:
                if e.errno != errno.EINPROGRESS:
                    raise
            self.connection_list.append(accepted)
            self.add_to_database(accepted, active)
            self.add_to_database(active, accepted)
            run = True
            while run:
                poller = util.build_poller(self.database, BUFF_SIZE)
                for fd, flag in poller.poll():
                    if flag & select.POLLIN:
                        try:                                
                            data = util.recv(self.database[fd]["socket"], BUFF_SIZE)
                            if data:
                                self.database[self.database[fd]["peer"]]["buff"] += data
                            else:
                                self.connection_list.pop(s)
                                s.close()
                        except disconnect.Disconnect as e:
                            run = False                        
                    if flag & (select.POLLHUP | select.POLLERR):
                        self.connection_list.pop(s)
                        s.close()
                    if flag & select.POLLOUT:
                        if self.database[fd]["buff"] != "":  
                            util.send(self.database[fd]["socket"], self.database[fd]["buff"])
                            self.database[fd]["buff"] = ""
            for s in self.connection_list:
                s.close()
        except:
            for s in self.connection_list:
                s.close()
            raise