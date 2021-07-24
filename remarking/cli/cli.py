import inspect
import logging
import os
import sys
import typing as T

import click
from click_help_colors import HelpColorsGroup

import remarking.cli.commands as commands_module
from remarking.cli import common
from remarking.cli import list as list_
from remarking.cli import writer_command, writer_command_runner
from remarking.storage import sqlalchemy_storage
from remarking.storage import storage as storage_

_BUG_FILING_URL = "https://github.com/sabidib/remarking/issues/new/choose"


class FileBugExceptionWrapper(Exception):
    """ Thrown from another exception to indicate to the user they should file a bug """

    def __init__(self) -> None:
        super().__init__(
            "If you have run into an exception during "
            f"normal usage please copy the exeption and then file a bug here: {_BUG_FILING_URL}")


def exception_wrapper(func: T.Any) -> T.Any:
    """ Used to re-throw all non-click exceptions with a FileBugExceptionWrapper """
    main_command_func = func.main

    def _wrapper(*args: T.Any, **kwargs: T.Any) -> T.Any:
        """ The wrapper """
        try:
            return main_command_func(*args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            if not isinstance(exc, (click.ClickException)):
                raise FileBugExceptionWrapper from exc
        return None

    func.main = _wrapper
    return func


@exception_wrapper
@click.group(
    cls=HelpColorsGroup,
    context_settings={
        "help_option_names": ["-h", "help", "--help"],
        "auto_envvar_prefix": "HIGHLIGHTS"
    },
    **common.help_color_options()
)
@click.version_option(package_name="remarking")
@click.option("-v", "--verbose", count=True, envvar="DEBUG", help="Increase logging level.")
@click.pass_context
def command_line(ctx: click.Context, verbose: int) -> None:
    """ Remarking is a tool for extracting higlights from reMarkable documents.

    Remarking accepts takes a list of documents or folders and downloads documents recursively.

    For each document, an extractor is applied, producing a list of highlights that are then output by a writer.

    A one-time code from https://my.remarkable.com/device/connect/desktop is required
    to download documents from the remarkable cloud.

    The simplest example is processing highlights and outputting them as a json blob.

    \b
    Example:
        remarking run json --token <mytoken> books
        {
          "documents": [
                {
                  "id": "1c1b93ec-73db-4dcd-a24c-25971fa6346e",
                  "name": "Through the Looking-Glass",
                  "parent": "598...
                } ...
            ],
            "highlights": [
                {
                  "document_id": "1c1b93ec-73db-4dcd-a24c-25971fa6346e",
                  "text": "The poor King looked puzzled and unhappy",
                  "page_number": 17 ...
                }
            ]
        }

    You can also sync highlights with a database using the persist sub-command.

    persist will only run on documents modified since the last run and will
    only output new highlights. This is useful for syncing with a database.

    For more examples check out the docs at: https://remarking.readthedocs.io/en/latest/

    Learn more with `remarking run --help`
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    if verbose > 0:
        click.echo(f"Verbosity: {verbose}", err=True)
        logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            level=logging.DEBUG if verbose > 0 else logging.WARNING)


@click.group(
    cls=HelpColorsGroup,
    **common.help_color_options()
)
@click.option("--sqlalchemy",
              type=str,
              required=True,
              nargs=1,
              default="sqlite:///remarking_database.sqlite3",
              envvar="REMARKING_SQLALCHEMY",
              show_envvar=True,
              help="When set to a sqlachemy connection string will save metadata about documents,"
              "document history and highlights across executions. This can also be a file whose contents"
              "are a connection string."
              )
@click.pass_context
def persist(ctx: click.Context, sqlalchemy: str) -> None:
    """ Produce new highlights since last execution.

    Extract highlights from the passed COLLECTION-NAMES.

    persist will only download documents that are new or have recently been changed since
    the last execution of persist.

    The specified extractors are run on each document and the highlights are
    processed by the specified output writer.

    persist uses a database specified by the `--sqlalchemy` argument to manage state
    and keep track of documents' last modified.

    The writer options of this command will only output the newest highlights that were
    found.

    persist is useful for periodically syncing highlights to a database.

    Keep in mind that the `--sqlalchemy` argument accepts any valid sqlachemy
    connection string. This means you may sync directly with a database of your choosing.

    To learn more about sqlalchemy connection string check out

    https://docs.sqlalchemy.org/en/latest/core/engines.html

    \b
    Example:
        remarking run --sqlalchemy sqlite:///database.sqlite3 json --token <mytoken> books
        {
          "documents": [
                {
                  "id": "1c1b93ec-73db-4dcd-a24c-25971fa6346e",
                  "name": "Through the Looking-Glass",
                  "parent": "598...
                } ...
            ],
            "highlights": [
                {
                  "document_id": "1c1b93ec-73db-4dcd-a24c-25971fa6346e",
                  "text": "The poor King looked puzzled and unhappy",
                  "page_number": 17 ...
                }
            ]
        }

    This creates a file named `database.sqlite3` in the current directory and uses that
    to manage state across runs. It then downloads any new documents in the books directory
    from the reMarkable cloud and processes them to extract highlights. If you ran this command
    again without making changes to the document you would have no new highlights.

    For more examples check out the docs at: https://remarking.readthedocs.io/en/latest/

    Learn more with `remarking persist json --help`

    """
    ctx.ensure_object(dict)
    if sqlalchemy is not None:
        source = ctx.get_parameter_source("sqlalchemy")
        if os.path.exists(sqlalchemy) and os.path.isfile(sqlalchemy):
            with open(sqlalchemy, "r") as file_p:
                sqlalchemy = file_p.read().strip()
        ctx.obj["source"] = source
    else:
        ctx.fail(click.style("Missing option '--sqlalchemy'. "
                             "Use `remarking run` to run without persistent storage."))
        sys.exit(1)
    storage = sqlalchemy_storage.SqlAlchemyStorage(sqlalchemy)
    ctx.obj["storage"] = storage


@click.group(
    cls=HelpColorsGroup,
    **common.help_color_options()
)
@click.pass_context
def run(ctx: click.Context) -> None:
    """ Produces highlights for the passed folders and documents

    Extract highlights from the passed COLLECTION-NAMES.

    run will download the documents and folders recursively and run the specified extractors
    on each document.

    The resulting highlights are output using the specified writer command.

    \b
    Example:
        remarking run json --token <mytoken> books
        {
          "documents": [
                {
                  "id": "1c1b93ec-73db-4dcd-a24c-25971fa6346e",
                  "name": "Through the Looking-Glass",
                  "parent": "598...
                } ...
            ],
            "highlights": [
                {
                  "document_id": "1c1b93ec-73db-4dcd-a24c-25971fa6346e",
                  "text": "The poor King looked puzzled and unhappy",
                  "page_number": 17 ...
                }
            ]
        }

    This command produces highlights for all the documents in the book directory
    on the reMarkable cloud.

    For more examples check out the docs at: https://remarking.readthedocs.io/en/latest/

    Learn more with `remarking persist json --help`
    """
    ctx.ensure_object(dict)
    ctx.obj["source"] = click.core.ParameterSource.DEFAULT
    ctx.obj["storage"] = storage_.NoStorage()


@click.command(name="help")
@click.pass_context
def help_(ctx: click.Context) -> None:
    """ Print help """
    with click.Context(ctx.parent) as parent_ctx:  # type: ignore
        click.echo(command_line.get_help(parent_ctx))


@click.command(name="bug")
def bug() -> None:
    """ File a bug """
    print(f"You can file a bug here: {_BUG_FILING_URL}")


WRITER_OUTPUT_CLASSES = []

for name, module in common.import_submodules(commands_module).items():
    for _, class_ in inspect.getmembers(module, predicate=inspect.isclass):
        if issubclass(class_, writer_command.WriterCommand) and class_ != writer_command.WriterCommand:
            WRITER_OUTPUT_CLASSES.append(class_)

writer_command_registration_handler = writer_command_runner.WriterCommandRegistrationHandler(
    [run, persist]
)

for writer_command in WRITER_OUTPUT_CLASSES:
    writer_command_registration_handler.register_writer_command(writer_command)  # type: ignore


command_line.add_command(run, "run")
command_line.add_command(persist, "persist")
command_line.add_command(list_.list_, "list")
command_line.add_command(help_, "help")
command_line.add_command(bug, "bug")
