""" Main entrypoint """


import click
from click_help_colors import HelpColorsCommand, HelpColorsGroup
from tabulate import tabulate

from remarking.cli import common, log


@click.group(
    name="list",
    cls=HelpColorsGroup,
    **common.help_color_options()
)
@click.pass_context
def list_(ctx: click.Context) -> None:
    """ List useful information """
    ctx.ensure_object(dict)
    ctx.obj['logger'] = log.CommandLineLogger(spinners_enabled=False, quiet=False)


@list_.command(
    cls=HelpColorsCommand,
    **common.help_color_options()
)
@click.pass_context
def extractors(ctx: click.Context) -> None:
    """ List extractors """
    logger = ctx.obj['logger']
    logger.echo(tabulate([(key, value.description) for key, value in common.get_extractor_mappings().items()],
                         headers=['extractor_name', 'extractor_description'],
                         tablefmt="grid"))


@list_.command(
    cls=HelpColorsCommand,
    **common.help_color_options()
)
@click.pass_context
def columns(ctx: click.Context) -> None:
    """ List normalized column names """
    logger = ctx.obj['logger']
    for column in common.generate_column_choices():
        logger.echo(column)
