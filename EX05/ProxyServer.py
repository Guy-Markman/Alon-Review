#The proxy server we will creat
import socket
import select


class ProxyServer(object):
    # port_active_connect: The port that our active side will connect with
    # port_passive_bind: The port that our passive side will bind to
    def __init__(self, host, port_active_connect, port_passive_bind):
        self.connection_list=[]
        
        self.passive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.passive.bind((host, port_passive_bind))
        self.passive.listen(1)
        
        self.active = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active.bind((host, port_active_connect))
        
        self.poller = select.poll()
    
    def connect(self, connect_address, connect_port)
        self.active.connect((connect_address, connect_port))
        
        accepted, addr = s.accept()
        self.connection_list.append(accepted)

    
        
        