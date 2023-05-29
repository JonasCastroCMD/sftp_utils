import json
import sys

from ..utils import to_snake_case


class Config:
    def __init__(self, **kwargs):
        self.port = 22

        # Fix naming convention
        kwargs_ = {}
        for kwarg in kwargs:
            kwargs_[to_snake_case(kwarg)] = kwargs[kwarg]

        required_arguments = [
            "name",
            "host",
            "remote_path",
            "username",
        ]

        for arg in required_arguments:
            if arg not in kwargs_:
                print(f"The argument `{arg}` is required.")
                sys.exit()

        for arg in kwargs_:
            self.__setattr__(arg, kwargs_[arg])

    @staticmethod
    def load_from_file(file_path):
        with open(file_path, "r") as f:
            return Config(**json.loads(f.read()))

    def save_to_file(self, file_path):
        with open(file_path, "w") as f:
            return f.write(self.__str__())

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)
