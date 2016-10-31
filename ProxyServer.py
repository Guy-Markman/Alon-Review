#The proxy server we will creat
import socket
import select


class ProxyServer(object):
    def __init__(self, host, port_active, port_passive):
        self.passive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.passive.bind((host, port_passive))
        self.passive.listen(1)
        
        self.active = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active.bind((host, port_active))
        
        self.poller = select.poll()
    def main(self, address_active_tupple):
        
        
        
        
        