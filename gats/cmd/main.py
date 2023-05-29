import argparse
import json
import os
import importlib

SOURCE_DIR = os.path.dirname(__file__)


def initialize_parser():
    parser_data_file_path = os.path.join(SOURCE_DIR, "parser_data.json")

    with open(parser_data_file_path, "r") as f:
        parser_data = json.loads(f.read())

    parser = argparse.ArgumentParser(prog=parser_data["prog"])
    subparsers = parser.add_subparsers(required=True, dest="subcommand")
    subcommands = parser_data["subcommands"]

    for subcommand, operations in subcommands.items():
        subcommand_parser = subparsers.add_parser(subcommand)
        subcommand_subparsers = subcommand_parser.add_subparsers(
            required=True, dest="operation"
        )

        for operation, arguments in operations.items():
            operation_parser = subcommand_subparsers.add_parser(operation)

            for argument in arguments:
                args = argument["args"] if "args" in argument else []
                kwargs = argument["kwargs"] if "kwargs" in argument else {}
                operation_parser.add_argument(*args, **kwargs)

    return parser


def main():
    parser = initialize_parser()
    args = parser.parse_args()

    module_name = f"gats.cmd.subcommands.{args.subcommand}.{args.operation}"
    module = importlib.import_module(module_name)
    module.Operation.run(args)


if __name__ == "__main__":
    main()
