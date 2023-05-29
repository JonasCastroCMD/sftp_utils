import paramiko


class ParamikoSSH:
    def __init__(self, config):
        self.config = config

    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        options = {
            "port": self.config.port,
            "username": self.config.username,
            "allow_agent": True,
        }

        if "password" in self.config.__dict__:
            options["password"] = self.config.password

        self.client.connect(
            self.config.host,
            **options,
        )

    def open_sftp(self):
        return self.client.open_sftp()

    def close(self):
        self.client.close()
