import importlib
from multiprocessing.connection import Listener
from threading import Thread
import sys
import traceback

from .commands import Commands  # noqa


class Server:
    AUTHKEY = b"TODO: Remove authkey because idk how to use it"

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.authkey = Server.AUTHKEY

    def run(self):
        address = (self.host, self.port)
        try:
            listener = Listener(address, authkey=self.authkey)
        except OSError:
            return print(f"The {address=} is already in use")

        while True:
            conn = listener.accept()
            address = listener.last_accepted
            print(f"Connection accepted from {address}")

            t = Thread(target=self.handle_connection, args=(conn, address))
            t.start()

        listener.close()

    def handle_connection(self, conn, address):
        global Commands
        cmd = Commands(conn)

        while True:
            try:
                method, args, kwargs = conn.recv()

                print(method, args, kwargs)

                if method == "reload_commands":
                    module = importlib.reload(
                        sys.modules["gats.server.commands"],
                    )

                    Commands = module.Commands
                    cmd = Commands(conn)
                else:
                    cmd.__getattribute__(method)(*args, **kwargs)
            except EOFError:
                print(f"{address} disconnected")
                break
            except:  # noqa
                print(traceback.format_exc())
                break

        conn.close()
