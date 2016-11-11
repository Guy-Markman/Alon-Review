# The proxy server we will creat
import socket
import select

READ_WRITE = select.POLLIN | select.POLLHUP | select.POLLERR | select.POLLOUT


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

    def proxy(self, args):
        while True:
            build_poller()
            events = self.poller.poll()
