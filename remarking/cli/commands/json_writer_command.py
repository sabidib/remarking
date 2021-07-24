
import datetime
import json
import typing as T
from typing import List

from remarking import models
from remarking.cli import log
from remarking.cli import writer as writer_
from remarking.cli import writer_command


def json_serial(obj: T.Any) -> T.Any:
    """JSON serializer for objects not serializable by default json code."""

    if isinstance(obj, (datetime.datetime)):
        return int(obj.timestamp())  # convert to unix ts
    raise TypeError("Type %s not serializable" % type(obj))


class JSONWriter(writer_.Writer):
    """ Write a JSON string representing the documents and highlights extracted.

        The JSON string resembles:

        .. code-block:: json

            {
              "documents": [
                {
                  "id": "235c7b66-c048-4639-ae89-8b2d60e3263b",
                  "version": 3,
                  "modified_client": 1626731660,
                  "type": "DocumentType",
                  "name": "Through the Looking Glass",
                  "current_page": 0,
                  "bookmarked": false,
                  "parent": "002de508-09db-4e25-8714-aedf6c484363"
                }
              ],
              "highlights": [
                {
                  "hash": "0e0e22dac038605e8ad32d9104525ff767ddf871689fd92a7adcfae4",
                  "document_id": "235c7b66-c048-4639-ae89-8b2d60e3263b",
                  "text": "Alice was sitting curled up in a corner of the great arm-chair",
                  "page_number": 11,
                  "extracted_at": 1626976202,
                  "extraction_method": "RemarkableHighlightExtractor"
                }
              ]
            }

        :param documents: The list of documents to generate a json string for.
        :param highlights: The list of highlights to generate a json string for.
    """

    def __init__(self, documents: List[models.Document], highlights: List[models.Highlight]) -> None:
        self.data = {
            'documents': [doc.to_dict() for doc in documents],
            'highlights': [highlight.to_dict() for highlight in highlights]
        }

    def write(self, logger: log.CommandLineLogger) -> None:
        json_string = json.dumps(self.data, default=json_serial)
        logger.output_result(json_string + '\n')


class JSONWriterCommand(writer_command.WriterCommand):
    """ The writer command implementation for the ``json`` output writer. """

    def name(self) -> str:
        return "json"

    def options(self) -> List[writer_command.ClickOption]:
        return []

    def long_description(self) -> str:
        return "Output highlights and documents as JSON"

    def short_description(self) -> str:
        return "Output highlights and documents as JSON"

    def writer(self,
               documents: List[models.Document],
               highlights: List[models.Highlight],
               **kwargs: T.Any) -> writer_.Writer:
        return JSONWriter(documents, highlights)
