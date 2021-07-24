import typing as T
from typing import List

import click
from tabulate import tabulate

from remarking import models
from remarking.cli import common, log
from remarking.cli import writer as writer_
from remarking.cli import writer_command


# pylint: disable=line-too-long
class TableWriter(writer_.Writer):
    """ Writes normalized documents and highlights to a simple table.

        Resembles:

        .. code-block:: text

                    highlight_text                                                    highlight_page_number  document_name
            --------------------------------------------------------------  -----------------------  -------------------------
            Alice was sitting curled up in a corner of the great arm-chair                       11  Through the Looking Glass

        :param documents: The list of documents to generate a table for.
        :param highlights: The list of highlights to generate a table for.
        :param columns: The columns to print for the table. A list of columns can be found by running
                        ``remarking list columns``
        :param truncate: If the ``highligh_text`` column should be truncated.
        :param print_plain: If a plain table with only spaces and new lines should be printed.

    """

    def __init__(self,
                 documents: List[models.Document],
                 highlights: List[models.Highlight],
                 columns: T.Optional[List[str]] = None,
                 truncate: bool = True,
                 print_plain: bool = False) -> None:
        self.truncate = truncate
        self.print_plain = print_plain
        self.highlights, self.headers = common.get_column_filtered_highlights_and_header(documents, highlights, columns)

    def write(self, logger: log.CommandLineLogger) -> None:
        if self.print_plain:
            logger.output_result(tabulate(self.highlights, headers="keys", tablefmt="plain") + '\n'
                                 if self.highlights else "")
        else:
            if self.truncate:
                for highlight in self.highlights:
                    text = highlight['highlight_text']
                    highlight['highlight_text'] = text[0:100] + ("..." if len(text) > 99 else "")
                for highlight in self.highlights:
                    text = highlight['document_name']
                    highlight['document_name'] = text[0:100] + ("..." if len(text) > 99 else "")
            logger.output_result(tabulate(self.highlights, headers="keys", tablefmt="simple") + '\n'
                                 if self.highlights else "")


class TableWriterCommand(writer_command.WriterCommand):
    """ The writer command implementation for the ``table`` output writer."""

    def name(self) -> str:
        return "table"

    def options(self) -> List[writer_command.ClickOption]:
        return common.column_based_output_options + [
            click.option("--plain/--no-plain",
                         "print_plain",
                         default=False,
                         help="Output one data entry per line."
                          ),
            click.option("--truncate/--no-truncate",
                         "do_truncate",
                         default=True,
                         help="Truncate results when printing plain"
                          )
        ]

    def long_description(self) -> str:
        return """Output highlights normalized with documents as a table.

Check out `remarking list columns` for a list of columns to choose from
for the `--columns` option.
    """

    def short_description(self) -> str:
        return "Output highlights normalized with documents as a table"

    def writer(self,
               documents: List[models.Document],
               highlights: List[models.Highlight],
               **kwargs: T.Any) -> writer_.Writer:
        columns = kwargs['columns']
        do_truncate = kwargs['do_truncate']
        print_plain = kwargs['print_plain']
        return TableWriter(documents, highlights, columns, do_truncate, print_plain)
