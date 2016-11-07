#Util models for all EX05
import fcntl

def set_non_blocking(Fd):
    fcntl.fcntl(
        Fd,
        fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK
    )
   

def fd_to_socket (server):
    return fd_to_socket = { server.fileno(): server,
               }