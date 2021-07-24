import csv
import io
import typing as T
from typing import List

import click

from remarking import models
from remarking.cli import common, log
from remarking.cli import writer as writer_
from remarking.cli import writer_command


class CSVWriter(writer_.Writer):
    """ Writes normalized documents and highlights to csv table.

        Resembles:

        .. code-block:: text

            highlight_text,highlight_page_number,document_name
            Alice was sitting curled up in a corner of the great arm-chair,11,Through the Looking Glass

        :param documents: The list of documents to generate a csv for.
        :param highlights: The list of highlights to generate a csv for.
        :param columns: The columns to print for the csv. A list of columns can be found by running
                        ``remarking list columns``
        :param delimiter: The delimiter to use for the csv.

    """

    def __init__(self,
                 documents: List[models.Document],
                 highlights: List[models.Highlight],
                 columns: T.Optional[List[str]] = None,
                 delimiter: str = None) -> None:
        self.delimiter = delimiter or ","
        self.columns = columns
        self.highlights, self.headers = common.get_column_filtered_highlights_and_header(documents, highlights, columns)

    def write(self, logger: log.CommandLineLogger) -> None:
        output = io.StringIO(newline='')
        writer = csv.DictWriter(output, delimiter=self.delimiter, fieldnames=self.headers)
        writer.writeheader()
        writer.writerows(self.highlights)
        logger.output_result(output.getvalue())


class CSVWriterCommand(writer_command.WriterCommand):
    """ The writer command implementaton for the ``csv`` output writer. """

    def name(self) -> str:
        return "csv"

    def options(self) -> List[writer_command.ClickOption]:
        return common.column_based_output_options + [click.option(
            "--delimiter",
            default=",",
            help="Delimiter to use to split columns"
        )]

    def long_description(self) -> str:
        return """Output highlights normalized with documents as csv.

Check out `remarking list columns` for a list of columns to choose from
for the `--columns` option.

    """

    def short_description(self) -> str:
        return "Output highlights normalized with documents as CSV"

    def writer(self,
               documents: List[models.Document],
               highlights: List[models.Highlight],
               **kwargs: T.Any) -> writer_.Writer:
        delimiter = kwargs['delimiter']
        columns = kwargs['columns']
        return CSVWriter(documents, highlights, columns, delimiter)
