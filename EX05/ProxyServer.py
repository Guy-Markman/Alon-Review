#The proxy server we will creat
import socket
import select


class ProxyServer(object):
    def __init__(self, host, bind_passive, bind_active):
        self.connection_list=[]
        
        self.passive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.passive.bind((host, bind_passive))
        self.passive.listen(1)
        
        self.active = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active.bind((host, bind_active))
        
        self.poller = select.poll()
    
    def connect(self, connect_address, connect_port)
        self.active.connect((connect_address, connect_port))
        
        accepted, addr = s.accept()
        self.connection_list.append(accepted)

    def proxy():
        