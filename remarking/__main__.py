""" Main entrypoint """
from remarking.cli import cli

__prog_name__ = "remarking"
__version__ = "0.1.0"


def main() -> None:
    return cli.command_line()  # pylint: disable=all
