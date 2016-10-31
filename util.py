#Util models for all EX05
import fcntl

def set_non_blocking(Fd):
    fcntl.fcntl(
        Fd,
        fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK
    )