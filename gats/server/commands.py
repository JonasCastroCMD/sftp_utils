class Commands:
    def __init__(self, conn):
        self.conn = conn

    def echo(self, *args, **kwargs):
        self.conn.send(
            {
                "method": "echo",
                "args": args,
                "kwargs": kwargs,
            }
        )

    def poggers(self, *args, **kwargs):
        print("def")
