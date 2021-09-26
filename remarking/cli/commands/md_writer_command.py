import typing as T
from typing import List

from remarking import Writer
from remarking import WriterCommand
from remarking import ClickOption
from remarking import CommandLineLogger
from remarking import Highlight
from remarking import Document

import click


class MDWriter(Writer):
    """ Writes a md document to output.  """

    def __init__(self,
                 documents: List[Document],
                 highlights: List[Highlight],
                 add_pages: bool,
                 ) -> None:
        self.documents = documents
        self.highlights = highlights
        self.add_pages = add_pages

    def write(self, logger: CommandLineLogger) -> None:
        """ Write to output. Invoked by remarking after extraction is ran on documents. """
        md_string = []
        for document in self.documents:
            # Write document name as the heading
            md_string.append("# " + document.name)

            for highlight in self.highlights:
                if highlight.document_id == document.id:
                    # Write highlight text as blockquote with page number in brackets at the end
                    if self.add_pages:
                        md_string.append(f'> "{highlight.text}" (p. {highlight.page_number})')
                    else:
                        md_string.append(f'> "{highlight.text}"')

        logger.output_result("\n\n".join(md_string) + "\n")




class MDWriterCommand(WriterCommand):
    """ MD Writer Command for: `md` output writer. """

    def name(self) -> str:
        """ Return the name of the command as referenced on the command line. """
        return "md"

    def options(self) -> List[ClickOption]:
        """ Return a list of click options to use for the command.

        The list can be constructed from the return value of :func:`click.option`.

        These options will be added to the default options for the run or persist command.
        """
        return [
            click.option("--pages/--no-pages",
                         "-p",
                         "add_pages",
                         default=False,
                         help="Add page numbers to blockquote"
                        )
        ]

    def long_description(self) -> str:
        """ The long description for your command. Shown when running ``--help`` """
        return "Returns documents and highlights as a Markdown document"

    def short_description(self) -> str:
        """ The short description of your command. """
        return "Output results as markdown"

    def writer(self,
               documents: List[Document],
               highlights: List[Highlight],
               **kwargs: T.Any) -> Writer:
        """ Parse options and return a configured instance of a concrete :class:`Writer` class. """
        add_pages = kwargs['add_pages']
        return MDWriter(documents, highlights, add_pages)