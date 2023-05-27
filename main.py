import argparse
import json
import os
import paramiko
from colorama import init
import sys
import psutil
import re

shell = psutil.Process(os.getppid()).name()

if shell != "bash.exe":
    init()

RED = '\033[1;31m'
GREEN = '\033[1;32m'
YELLOW = '\033[1;33m'
MAGENTA = '\033[1;35m'
CYAN = '\033[1;36m'
NC = '\033[0m'

def get_configs(args):
    config_folder = os.path.abspath(".vscode/")

    if(len(args.config) == 0):
        config_file_paths = [os.path.join(config_folder, 'sftp.json')]
    else:
        config_file_paths = map(lambda n: os.path.join(config_folder, f'sftp-{n}.json'), args.config)

    configs = []
    for config_file_path in config_file_paths:
        with open(config_file_path, "r") as f:
            config = json.loads(f.read())

        configs.append((config_file_path, config))

    return configs

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


    if(num_files_discarded > 0):
        print(f"{YELLOW}[Total de arquivos descartados: {num_files_discarded}]{NC}", flush=True)
    print(f"{YELLOW}[Total de arquivos modificados: {num_files_filtered}]{NC}", flush=True)

    if num_files_filtered == 0:
        return

    configs = get_configs(args)

    for config_file_path, config in configs:
        print(f"{YELLOW}[{config_file_path}]{NC}", flush=True)
        print(json.dumps(config, indent=4), flush=True)

        if not args.list_only:
            ssh = connect_ssh(config)
            sftp = ssh.open_sftp()

        if(num_files_discarded > 0):
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

def COMMAND_switch_config(args):
    config_name = args.config[0] if len(args.config) > 0 else None
    if(not config_name):
        return print(f"{RED}Eh necessario especificar a configuracao pelo nome{NC}")

    config_folder = os.path.join(os.getcwd(), '.vscode')
    link_path = os.path.join(config_folder, 'sftp.json')
    config_path = os.path.join(config_folder, f'sftp-{config_name}.json')

    if not os.path.isfile(config_path):
        return print(f"{RED}O arquivo `{config_path}` nao existe{NC}")

    os.system(f'ln -sf {config_path} {link_path}')

    with open(link_path, 'r') as f:
        print(f.read())

def COMMAND_define_config(args):
    regex = "env(\d+)-node(\d+)"

    if len(args.config) == 0:
        return print(f"{RED}Eh necessario pelo menos um nome de config no formato `{regex}`{NC}")

    for config_name in args.config:
        config_folder = os.path.join(os.getcwd(), '.vscode')
        matches = re.findall(regex, config_name)

        if len(matches) == 0:
            return print(f"{RED}Os nomes de config `{config_name}` nao correspondem com o regex `{regex}`{NC}")

        template = {
            "name": "Env{env} - Node {node}",
            "host": "node{node}.comdinheiro.com.br",
            "remotePath": "/replica/www/env{env}",
            "uploadOnSave": True,
            "protocol": "sftp",
            "port": 2768,
            "username": "root",
            "agent": "pageant"
        }

        for env, node in matches:
            config_path = os.path.join(config_folder, f'sftp-env{env}-node{node}.json')
            config = template.copy()
            config["name"] = config["name"].format(env=env, node=node)
            config["host"] = config["host"].format(node=node)
            config["remotePath"] = config["remotePath"].format(env=env)

            with open(config_path, 'w') as f:
                f.write(json.dumps(config, indent=4))

def COMMAND_delete_config(args):
    for config_name in args.config:
        config_path = os.path.join(os.getcwd(), '.vscode', f'sftp-{config_name}.json')
        os.remove(config_path)

def COMMAND_list_config(args):
    config_folder = os.path.join(os.getcwd(), '.vscode')
    regex = "env(\d+)-node(\d+)"

    for m in filter(lambda x: x, [re.search(regex, f) for f in os.listdir(config_folder)]):
        print(m[0])

def COMMAND_current_config(args):
    config_path = os.path.join(os.getcwd(), '.vscode', 'sftp.json')
    regex_name = "Env(\d+) - Node (\d+)"

    with open(config_path, "r") as f:
        config_raw = f.read()


    matches = re.findall(regex_name, config_raw)
    if(len(matches) == 0):
        return print(f"{RED}O arquivo {config_path} nao tem a opcao `name` no formato `{regex_name}`{NC}")

    env, node = matches[0]

    print(f'env{env}-node{node}')

PREFIX = "COMMAND_"

def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("command", choices=list(map(lambda x: x.removeprefix(PREFIX), filter(lambda x: x.startswith(PREFIX), globals().keys()))))
    parser.add_argument("--list-only", action="store_true", default=False)
    parser.add_argument("--from-stdin", action="store_true", default=False)
    parser.add_argument("--from-file")
    parser.add_argument("-c","--config", nargs='*', default=[])

    return parser.parse_args()

def main():
    args = get_arguments()

    globals()[PREFIX + args.command](args)

if __name__ == "__main__":
    main()