import functools
import typing as T
from typing import List, Type

import click
from click_help_colors import HelpColorsCommand

from remarking import models
from remarking import rmcloud as rmcloud_
from remarking.cli import common, extract, log, writer_command
from remarking.storage import storage as storage_


# TODO: this should be changed to the proper type...
def add_options(options: T.List[T.Callable[..., T.Any]]) -> T.Callable[..., T.Any]:
    """ Decorate a method with a list of `click.option` calls. """
    def _add_options(func: T.Any) -> T.Any:
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


def get_token(ctx: click.Context) -> T.Optional[str]:
    """ Retrieve reMarkable token via a prompt.

        If stdout or stderr is not a tty, then fail with an error, indicating the user should add the option.
    """
    if not log.isatty():
        ctx.fail(
            click.style("Missing option '-t' / '--token'. Cannot prompt for option. "
                        "Are you in non-interactive mode or piping?"))
    token = click.prompt("Enter your one-time auth token from my.remarkable.com", type=click.STRING, err=True)
    return token


def get_storage(ctx: click.Context, logger: log.CommandLineLogger) -> storage_.Storage:
    """ Retrieve previously set storage from a context object.

    If a storage object cannot be found we raise an error from click.

    Logs appropriate messages to logger.
    """
    storage = ctx.obj.get("storage")
    if storage is None:
        ctx.fail(click.style(
            "Could not find a storage object to use. Please file a bug using `highlights file`", fg='red'
        ))
    else:
        source = ctx.obj.get("source")
        if source is not None:
            if source.name == "ENVIRONMENT":
                logger.echo(click.style(f"Received storage option from {source.name}", fg="green"), err=True)
        else:
            logger.echo(click.style("Could not determine source of storage option.", fg="red"), err=True)

    return storage


def get_logger(ctx: click.Context, quiet: bool, output: T.Optional[T.IO] = None) -> log.CommandLineLogger:
    """ Construct the logger given a command context.

    If quiet is set the logger does not print.
    """
    verbose = ctx.obj['verbose']
    logger = log.CommandLineLogger(spinners_enabled=(verbose == 0), quiet=quiet, file_output=output)
    return logger


# TODO: Need to write the correct annotations
def highlight_output_command(short_help: str, help_: str, name: str) -> T.Any:
    """ Decorator for wrapping command line arguments for output commands."""

    def wrapper(func: T.Any) -> T.Any:
        @functools.wraps(func)
        @click.command(
            name=name,
            cls=HelpColorsCommand,
            short_help=short_help,
            help=help_,
            **common.help_color_options()
        )
        @add_options(common.core_run_options)
        @click.pass_context
        def command(ctx: click.Context,
                    token: str,
                    working_directory: str,
                    extractors: T.List[str],
                    collection_names: T.List[str],
                    output: T.Optional[T.IO],
                    quiet: bool,
                    **kwargs: T.Any) -> None:
            logger = get_logger(ctx, quiet, output)
            storage = get_storage(ctx, logger)
            try:
                rmcloud_.RMCloud("fake_token_for_checking_auth")
            except rmcloud_.AuthError:
                if token is None:
                    token = get_token(ctx)
            except rmcloud_.RenewAuthError:
                if token is None:
                    logger.echo(
                        click.style("Failed to renew auth for reMarkable cloud. Did you de-authorize remarking?\n"
                                    "Please enter a new one time auth code, or delete your ~/.rmapi file.",
                                    fg='red', bg="white"),
                        err=True
                    )
                    token = get_token(ctx)

            documents, highlights = extract.run_extract(
                logger, token, working_directory, extractors, collection_names, storage)

            func(documents, highlights, logger, **kwargs)

        # This is a bit of a hack, but let's use put highlight output command
        # at any position as a decorator.
        if hasattr(func, "__click_params__"):
            command.params.extend(func.__click_params__)

        return command
    return wrapper


class BadWriterCommandOptionException(RuntimeError):
    """ Raised when a WriterCommand did not provide an options list """


class WriterCommandRegistrationHandler():
    """ Used to register implementations of `writer_command.WriterCommand` with a list of command groups."""

    def __init__(self, command_groups: List[click.Group]) -> None:
        self._command_groups = command_groups

    def register_writer_command(self, command_cls: Type[writer_command.WriterCommand]) -> None:
        """
        Registers a class object that implements `writer_command.WriterCommand`

        with the command groups of this class.
        """
        writer_command_instance = command_cls()
        options = writer_command_instance.options()
        if options is None:
            raise BadWriterCommandOptionException(
                f"Found None for '{command_cls.__name__}.options()'. "
                "Did you forget to return the options list? If not, return an empty array."
            )

        @highlight_output_command(
            short_help=writer_command_instance.short_description(),
            help_=writer_command_instance.long_description(),
            name=writer_command_instance.name()
        )
        @add_options(options)
        def caller(documents: List[models.Document],
                   highlights: List[models.Highlight],
                   logger: log.CommandLineLogger,
                   **kwargs: T.Any) -> None:
            writer = writer_command_instance.writer(documents, highlights, **kwargs)
            writer.write(logger)

        for command_group in self._command_groups:
            command_group.add_command(caller, writer_command_instance.name())
