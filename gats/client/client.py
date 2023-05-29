from multiprocessing.connection import Client as MClient
from ..server import Server


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.authkey = Server.AUTHKEY

    def connect(self):
        self.conn = MClient(
            (self.host, self.port),
            authkey=self.authkey,
        )

    def send(self, method, *args, **kwargs):
        self.conn.send((method, args, kwargs))

    def recv(self):
        return self.conn.recv()

    def close(self):
        self.conn.close()
