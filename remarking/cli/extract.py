import logging
import sys
import typing as T
from typing import List

import click

from remarking import models
from remarking import rmcloud as rmcloud_
from remarking.cli import app as app_
from remarking.cli import common, log
from remarking.highlight_extractor import highlight_extractor
from remarking.storage import storage as storage_


def run_extract(logger: log.CommandLineLogger,
                token: str,
                working_directory: str,
                extractors: T.List[str],
                collection_names: T.List[str],
                storage: storage_.Storage
                ) -> T.Tuple[List[models.Document], List[models.Highlight]]:
    """ Run extraction of highlights.

    :param: token: reMarkable cloud one time use token.
    :param: working_directory: a directory to download highlights to and perform general file io in.
    :param: extractors: A list of named highlight extractors. The names should match those
                        in common.get_extractor_mappings(). They can be listed with the `list` subcommand
    :param: collection_names: A list of the names of folder and documents that highlights should be extracted from.
    :param: storage: an implementation of storage to persist highlight and document state.

    :returns: A list of highlights and their associated documents.
    """

    if not collection_names:
        logger.echo(click.style("Empty list of collection names passed", fg='red', bg='white'), err=True)

    logger.echo(click.style("Extractors", fg="green", bold=True) + f": {', '.join(extractors)}", err=True)
    logger.echo(click.style("Collections", fg="green", bold=True) + f": {' , '.join(collection_names)}", err=True)

    extractor_instances: List[highlight_extractor.HighlightExtractor] = []
    for extractor_name in extractors:
        logging.info(f"Creating extractor {extractor_name}")
        extractor_instances.append(common.get_extractor_mappings()[extractor_name].instance)

    spinner = logger.spinner(text="Connecting to RM cloud", spinner="bouncingBar")
    spinner.start()
    rmcloud: T.Optional[rmcloud_.RMCloud] = None
    try:
        rmcloud = rmcloud_.RMCloud(token)
    except rmcloud_.AuthError:
        spinner.fail()
        logger.echo(click.style("Failed to connect to the Remarkable Cloud, is the token correct?", fg="red"))
        sys.exit(1)
    spinner.succeed("Connected to RM cloud.")

    app = app_.App(rmcloud=rmcloud, storage=storage, extractors=extractor_instances, logger=logger)
    documents, highlights = app.run_app(working_directory, collection_names)
    return documents, highlights
