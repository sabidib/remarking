import importlib
import inspect
import pkgutil
import typing as T
import uuid
from typing import Dict, List, Tuple

import click

import remarking.highlight_extractor as highlight_extractor_modules
from remarking import models
from remarking.highlight_extractor import highlight_extractor


def import_submodules(package: T.Any, recursive: bool = True) -> T.Any:
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for _, package_name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + package_name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results


def get_extractor_mappings() -> T.Dict[str, highlight_extractor.ExtractorData]:
    """ Returns mapping of extractor name to instances of :class:`ExtractorData` """
    mapping = {}

    for _, module in import_submodules(highlight_extractor_modules).items():
        for _, class_ in inspect.getmembers(module, predicate=inspect.isclass):
            if issubclass(class_,
                          highlight_extractor.HighlightExtractor) and class_ != highlight_extractor.HighlightExtractor:
                extractor_data_list = class_.get_extractor_instance_data()
                for extractor_data in extractor_data_list:
                    mapping[extractor_data.extractor_name] = extractor_data
    return mapping


def help_color_options() -> Dict[str, str]:
    """ Return color options for click-help """
    return {
        'help_headers_color': 'yellow',
        'help_options_color': 'green'
    }



# pylint: disable=unused-argument


def validate_extractors(ctx: click.Context, param: click.Parameter, value: T.Any) -> List[str]:
    """ Validate column argument against normalized column choices.

    Should be called as a click callback.
    """
    processed_extractors = value.replace(" ", "").split(",")
    valid_extractors = list(get_extractor_mappings().keys())
    for extractor in processed_extractors:
        if extractor not in valid_extractors:
            raise click.BadParameter(
                f"extractor '{extractor}' is not in list of extractors. "
                f"Run `remarking list extractors` for more info on the following valid extractors: {valid_extractors}"
            )
    return processed_extractors


# pylint: disable=unused-argument
def validate_columns(ctx: click.Context, param: click.Parameter, value: str) -> List[str]:
    """ Validate column argument against normalized column choices.

    Should be called as a click callback.
    """
    processed_columns = value.replace(" ", "").split(",")
    valid_columns = list(generate_column_choices())
    for column in processed_columns:
        if column not in valid_columns:
            raise click.BadParameter(
                f"column '{column}' is not in list of columns. "
                f"run `remarking list columns` for more info on the following valid columns: {valid_columns}"
            )
    return processed_columns


column_based_output_options = [
    click.option("--columns",
                 default="highlight_text,document_name,highlight_page_number",
                 type=str,
                 show_default=True,
                 callback=validate_columns,
                 help="Comma delimited list of columns to print when using plain printing. "
                 "`remarking list columns` shows all available columns",
                  )
]

core_run_options = [
    click.option("-t",
                 "--token",
                 default=None,
                 show_envvar=True,
                 show_default=False,
                 help="One time auth token from for the reMarkable cloud. Needs only be specified once.",
                 envvar="REMARKING_TOKEN"
                 ),
    click.option("--extractors",
                 "-e",
                 default='remarkable',
                 type=str,
                 show_default=True,
                 callback=validate_extractors,
                 help="Comma delimited list of extractors to use. "
                 "Run `remarking list extractors` to see valid extractors."
                  ),
    click.option("--output",
                 "-o",
                 type=click.File('w', lazy=True),
                 default=None,
                 help="Output highlights to the given file"),
    click.option("--working-directory",
                 "-w",
                 type=click.Path(exists=False,
                                 file_okay=False,
                                 dir_okay=True,
                                 writable=True,
                                 readable=True,
                                 resolve_path=True,
                                 allow_dash=True),
                 default=lambda: f"/tmp/remarkable_highlights/{uuid.uuid4()}",
                 show_default="A randomly generated path within /tmp/",
                 help="Working directory where files will be downloaded and highlights generated."
                  ),
    click.option("-q", "--quiet", is_flag=True, help="Print nothing."),
    click.argument("collection-names", nargs=-1)
]


def generate_normalized_column_mappings() -> Dict[str, T.Dict[str, str]]:
    """ Generate mappings for model column names to normalized column names """
    dummy_highlight = models.Highlight()
    dummy_document = models.Document()
    return {
        "highlight": {key: f'highlight_{key}' for key in dummy_highlight.to_dict().keys()},
        "document": {key: f'document_{key}' for key in dummy_document.to_dict().keys()}
    }


def generate_column_choices() -> T.List[str]:
    """ Generate columns names for normalized mappings"""
    mappings = generate_normalized_column_mappings()
    return [
        *list(mappings['highlight'].values()),
        *list(mappings['document'].values())
    ]


def get_column_filtered_highlights_and_header(
    documents: List[models.Document],
    highlights: List[models.Highlight],
    columns: T.Optional[List[str]] = None
) -> Tuple[List[Dict[str, str]], List[str]]:
    """ Return the normalized highlights filtered to the passed columns, also return the headers for
    the normalized columns.

    If columns is empty all normalized columns are used.

    Returns headers even if normalized highlight is empty.

    """

    mappings = generate_normalized_column_mappings()
    headers = [
        *mappings['highlight'].values(),
        *mappings['document'].values(),
    ]
    normalized_highlights = normalize_highlights_and_documents(documents, highlights)
    if columns is not None:
        keys_to_remove = [key for key in headers if key not in columns]
        for key in keys_to_remove:
            headers.remove(key)

        for highlight in normalized_highlights:
            for key in keys_to_remove:
                highlight.pop(key)

    return normalized_highlights, headers


class MissingDocumentException(Exception):
    """ Exception raised if a document cannot be found for a highlight when normalizing highlights with documents """

    def __init__(self, doc_id: str) -> None:
        super().__init__(self, f"Could not find document with id {doc_id}")


def normalize_highlights_and_documents(documents: List[models.Document],
                                       highlights: List[models.Highlight]) -> List[Dict[str, T.Any]]:
    """ Join a list of documents and highlights on models.Document.id == models.Highlight.document_id

    If a highlight has no matching document, an exception is thrown.
    """
    mappings = generate_normalized_column_mappings()
    documents_dict = [doc.to_dict() for doc in documents]
    highlights_dict = [highlight.to_dict() for highlight in highlights]

    document_lookup = {doc['id']: doc for doc in documents_dict}

    normalized_highlights = []
    for highlight in highlights_dict:
        new_highlight = {
            mappings['highlight'][key]: value
            for key, value in highlight.items()
        }
        if highlight['document_id'] not in document_lookup:
            raise MissingDocumentException(highlight['document_id'])
        document = document_lookup[highlight['document_id']]
        new_document = {
            mappings['document'][key]: value
            for key, value in document.items()
        }
        new_highlight.update(new_document)
        normalized_highlights.append(new_highlight)

    return normalized_highlights
