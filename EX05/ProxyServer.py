#!/usr/bin/env python
# The proxy server we will creat
import errno
import select
import socket
import traceback

CLOSE, PROXY, ACTIVE = range(3)


class Disconnect(RuntimeError):

    def __init__(self):
        super(Disconnect, self).__init__("Disconnect")


class ProxyServer(object):
    _database = {}

    def __init__(
        self,
        buff_size,
    ):
        self._buff_size = buff_size
        self._run = True

    def terminate(self):
        self._run = False

    def add_proxy(
        self,
        our_address=("localhost", 8080),
        connect_address=("localhost", 8061),
    ):
        s = self._creat_nonblocking_socket()
        s.bind(our_address)
        s.listen(1)
        self._add_to_database(s, state=PROXY, address=connect_address)

    def _creat_nonblocking_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)
        return s

    def _add_to_database(
        self,
        s,
        peer=None,
        state=ACTIVE,
        address=None
    ):
        self._database[s.fileno()] = {
            "socket": s,  # our socket
            "buff": "",  # Buff to send to socket

            # Peer in database
            "peer": None if peer is None else peer.fileno(),

            "state": state,  # Proxy, active or close
            "connect_address": address,  # For proxy only, where to connect
        }

    def _close_fd(self, fd):
        entry = self._database[fd]
        peer_fd = entry["peer"]

        if peer_fd is not None:
            peer_database = self._database[peer_fd]
            peer_database.update({
                "peer": None,
                "state": CLOSE
            })
        entry["socket"].close()
        self._database.pop(fd)

    def _connect_both_sides(self, entry):
        accepted = None
        active = None
        try:
            accepted, addr = entry["socket"].accept()
            accepted.setblocking(0)
            active = self._creat_nonblocking_socket()
            try:
                active.connect(entry["connect_address"])
            except socket.error as e:
                if e.errno != errno.EINPROGRESS:
                    raise

            self._add_to_database(accepted, active, state=ACTIVE)
            self._add_to_database(active, accepted, state=ACTIVE)
        except Exception as e:
            traceback.print_exc()
            if accepted is not None:
                accepted.close()
            if active is not None:
                active.close()

    def _build_poller(self):
        poller = select.poll()
        for entry in self._database.values():
            events = select.POLLERR
            if entry["state"] == CLOSE:
                events |= select.POLLOUT
            elif entry["state"] == PROXY:
                events |= select.POLLIN
            elif entry["state"] == ACTIVE:
                if entry["buff"]:
                    events |= select.POLLOUT
                fd_peer = entry["peer"]
                if (
                    fd_peer is not None and
                    len(self._database[fd_peer]) < self._buff_size
                ):
                    events |= select.POLLIN
            else:
                raise RuntimeError("Corrupted database")
            poller.register(entry["socket"], events)

        return poller

    def proxy(self, args):
        while self._database:
            try:
                if not self._run:
                    for fd in self._database:
                        self._database[fd]["state"] = CLOSE
                for fd in self._database.keys():
                    entry = self._database[fd]
                    if entry["state"] == CLOSE and entry["buff"] == "":
                        self._close_fd(fd)
                poller = self._build_poller()
                events = poller.poll()
                for fd, flag in events:
                    entry = self._database[fd]
                    if flag & select.POLLIN:
                        if entry["state"] == PROXY:
                            self._connect_both_sides(entry)
                        else:
                            self.recv(fd)

                    if flag & select.POLLHUP:
                        raise Disconnect()
                    if flag & select.POLLERR:
                        raise RuntimeError(
                            "Error condition happened on %s" % fd
                        )

                    if flag & select.POLLOUT:
                        self.send(entry)

            except select.error as e:
                if e[0] != errno.EINTR:
                    traceback.print_exc()
                    self._close_fd(fd)

            except Disconnect as e:
                traceback.print_exc()
                self._database[self._database[fd]["peer"]]["state"] = CLOSE
            except Exception as e:
                traceback.print_exc()
                self._close_fd(fd)

    def recv(self, entry):
        peer_entry = self.database[entry["peer"]]
        entry_socket = entry["socket"]
        while len(peer_entry) < self._buff_size:
            try:
                buff = entry_socket.recv(
                    self._buff_size - len(peer_entry["buff"])
                )
                if not buff:
                    if not peer_entry["buff"]:
                        raise Disconnect(entry.keys()[0])
                    break
                peer_entry["buff"] += buff
                break
            except socket.error as e:
                if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
                break

    def send(self, entry):
        entry_buff = entry["buff"]
        while entry_buff:
            try:
                entry_buff = entry_buff[entry["socket"].send(entry_buff):]
            except socket.error as e:
                if e.errno not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
                else:
                    break
