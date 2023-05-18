import argparse
import json
import os
import paramiko
from colorama import init
import sys
import psutil

shell = psutil.Process(os.getppid()).name()

if shell != "bash.exe":
    init()

RED = '\033[1;31m'
GREEN = '\033[1;32m'
YELLOW = '\033[1;33m'
MAGENTA = '\033[1;35m'
CYAN = '\033[1;36m'
NC = '\033[0m'

def get_sftp_config():
    sftp_config_file_path = os.path.abspath(".vscode/sftp.json")

    with open(sftp_config_file_path, "r") as f:
        config = json.loads(f.read())

    print(f"{YELLOW}[.vscode/sftp.json]{NC}", flush=True)
    print(json.dumps(config, indent=4), flush=True)

    return config

def connect_ssh(config):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"{YELLOW}[Conectando via SSH...]{NC}", flush=True)
    ssh.connect(
        config["host"],
        port=config["port"],
        username=config["username"],
        allow_agent=True
    )

    return ssh

def __upload_file(local_path, remote_path, args, sftp):
    sftp.put(local_path, remote_path)

def COMMAND_update_remote(args):
    inp = ""
    if args.from_stdin:
        inp = sys.stdin.read()
    elif args.from_file:
        with open(args.from_file, "r") as f:
            inp = f.read()

    files = list(set(inp.strip().split("\n")))

    files_path = list(map(lambda x: os.path.abspath(x), files))
    num_files = len(files_path)

    files_path_filtered = list(filter(lambda x: os.path.isfile(x), files_path))
    num_files_filtered = len(files_path_filtered)

    files_path_discarded = list(set(files_path) - set(files_path_filtered))
    num_files_discarded = num_files - num_files_filtered


    print(f"{YELLOW}[Total de arquivos descartados: {num_files_discarded}]{NC}", flush=True)
    print(f"{YELLOW}[Total de arquivos para atualizar: {num_files_filtered}]{NC}", flush=True)

    if num_files_filtered == 0:
        return

    config = get_sftp_config()

    if not args.list_only:
        ssh = connect_ssh(config)
        sftp = ssh.open_sftp()

    print(f"{YELLOW}[Lista de arquivos descartados]{NC}", flush=True)
    for i, local_path in enumerate(files_path_discarded):
        print(f"[{str(i+1).zfill(2)}/{str(num_files_discarded).zfill(2)}]{CYAN}[local: {local_path}]{NC}", flush=True)

    print(f"{YELLOW}[Lista de arquivos para atualizar]{NC}", flush=True)
    for i, local_path in enumerate(files_path_filtered):
        remote_path = os.path.join(config["remotePath"], os.path.relpath(local_path, os.getcwd())).replace("\\", "/")

        if not args.list_only:
            __upload_file(local_path, remote_path, args, sftp)

        print(f"[{str(i+1).zfill(2)}/{str(num_files_filtered).zfill(2)}]{CYAN}[local: {local_path}]{NC} -> {MAGENTA}[remote: {remote_path}]{NC}", flush=True)

    if not args.list_only:
        sftp.close()
        ssh.close()

PREFIX = "COMMAND_"

def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("command", choices=list(map(lambda x: x.removeprefix(PREFIX), filter(lambda x: x.startswith(PREFIX), globals().keys()))))
    parser.add_argument("--list-only", action="store_true", default=False)
    parser.add_argument("--from-stdin", action="store_true", default=False)
    parser.add_argument("--from-file")

    return parser.parse_args()

def main():
    args = get_arguments()

    globals()[PREFIX + args.command](args)

if __name__ == "__main__":
    main()