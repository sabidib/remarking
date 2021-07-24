from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import List

from remarking import models


@dataclass
class ExtractorData:
    """ Represents an extractor mapping entry.

        This is used by remarking to generate extractor choices for the end user.

        :param extractor_name:  The name of the extractor on the command line.
        :param instance: An instance of the extractor.
        :param description: A description for the extractor. This is shown when running
                            ``remarking list extractors``
    """
    extractor_name: str
    instance: 'HighlightExtractor'
    description: str


class HighlightExtractor(metaclass=ABCMeta):  # pylint: disable=too-few-public-methods
    """ Base class for highlight extractors.

        Extractors are run after documents are downloaded. remarking calls
        :meth:`HighlightExtractor.get_highlights` for each document downloaded.


        For example, :class:`RemarkableHighlightExtractor` is will extract the
        highlgihts from the built-in reMarkable highlighting functionality.
    """

    @classmethod
    @abstractmethod
    def get_extractor_instance_data(cls) -> List[ExtractorData]:
        """ Return a list of :class:`ExtractorData` instaces representing
            different run options for the extractor.
        """

    @abstractmethod
    def get_highlights(self, working_path: str, document: models.Document) -> List[models.Highlight]:
        """ Retrieve all highlights for document.

        :param working_path: The path on the operating system where all documents were downloaded. Documents
            are downloaded from the cloud and unzipped into this repository. For more information on the layout
            check out `<https://remarkablewiki.com/tech/filesystem#user_data_directory_structure>`_.

        :param document: The document to extract highlights for.

        :return: A list of highlights for the document.
        """


def clean_highlight_text(text: str) -> str:
    """ Return a cleaned version of the passed text. """
    to_replace = [
        ("“", "\""),
        ("‘", "'"),
        ("’", "'"),
        ("”", "\"")
    ]
    cleaned = text
    for replacements in to_replace:
        cleaned = cleaned.replace(replacements[0], replacements[1])
    return cleaned
