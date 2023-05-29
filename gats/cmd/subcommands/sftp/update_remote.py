import func_colors
import json
import os
import sys

from ....ssh import ParamikoSSH  # bruh
from ....config import Config  # bruh


class Operation:
    @classmethod
    def run(cls, args):
        c = func_colors.ColorContext()

        if args.input == "-":
            inp = sys.stdin.read()
        else:
            with open(args.input, "r") as f:
                inp = f.read()

        files = list(set(inp.strip().split("\n")))

        files_path = list(map(lambda x: os.path.abspath(x), files))
        num_files = len(files_path)

        files_path_filtered = list(
            filter(
                lambda x: os.path.isfile(x),
                files_path,
            )
        )
        num_files_filtered = len(files_path_filtered)

        files_path_discarded = list(set(files_path) - set(files_path_filtered))
        num_files_discarded = num_files - num_files_filtered

        if num_files_discarded > 0:
            print(
                c.yellow(
                    f"[Total de arquivos descartados: {num_files_discarded}]"
                ),  # noqa
                flush=True,
            )
        print(
            c.yellow(f"[Total de arquivos modificados: {num_files_filtered}]"),
            flush=True,
        )

        if num_files_filtered == 0:
            return

        # TODO: Use the client/server
        configs = cls.get_configs(args)

        for config_file_path, config in configs:
            print(c.yellow(f"[{config_file_path}]"), flush=True)
            print(config, flush=True)

            if not args.list_only:
                # TODO: Use the client/server
                ssh = ParamikoSSH(config)
                ssh.connect()
                sftp = ssh.open_sftp()

            if num_files_discarded > 0:
                print(c.yellow("[Lista de arquivos descartados]"), flush=True)
                for i, local_path in enumerate(files_path_discarded):
                    print(
                        f"[{str(i+1).zfill(2)}/{str(num_files_discarded).zfill(2)}]{CYAN}[local: {local_path}]{NC}",  # noqa
                        flush=True,
                    )

            print(c.yellow("[Lista de arquivos para atualizar]"), flush=True)  # noqa
            for i, local_path in enumerate(files_path_filtered):
                remote_path = os.path.join(
                    config.remote_path,
                    os.path.relpath(local_path, os.getcwd()),
                ).replace("\\", "/")

                if not args.list_only:
                    # TODO: Use the client/server
                    sftp.put(local_path, remote_path)

                print(
                    f"[{str(i+1).zfill(2)}/{str(num_files_filtered).zfill(2)}]"
                    + c.cyan(f"[local: {local_path}]"),  # noqa
                    "->",
                    c.magenta(f"[remote: {remote_path}]"),
                    flush=True,
                )

            if not args.list_only:
                sftp.close()
                ssh.close()

    @staticmethod
    def get_configs(args):
        config_folder = os.path.abspath(".vscode/")

        if len(args.config) == 0:
            config_file_paths = [os.path.join(config_folder, "sftp.json")]
        else:
            config_file_paths = map(
                lambda n: os.path.join(config_folder, f"sftp-{n}.json"),
                args.config,
            )

        configs = map(lambda c: (c, Config.load_from_file(c)), config_file_paths)

        return configs
