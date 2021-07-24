""" Application """
import itertools
import logging
import typing as T
from typing import Dict, List, Tuple

from remarking import models
from remarking import rmcloud as rmcloud_
from remarking.cli import log
from remarking.highlight_extractor import highlight_extractor
from remarking.storage import storage as storage_


class App():
    """ Main application class """

    def __init__(self,
                 rmcloud: rmcloud_.RMCloud,
                 extractors: List[highlight_extractor.HighlightExtractor],
                 logger: T.Optional[log.CommandLineLogger] = None,
                 storage: storage_.Storage = None,
                 ) -> None:
        self._rmcloud = rmcloud
        self._storage = storage or storage_.NoStorage()
        self._extractors = extractors
        self._logger = logger or log.CommandLineLogger(spinners_enabled=False, quiet=True)

    def run_app(self, working_path:
                str, collection_names: List[str]) -> Tuple[List[models.Document], List[models.Highlight]]:
        """ Run highlight extractor.

            working_path is used for temporary storage while the extractor is running.

            collection_names: A list of folder and document names to extract highlights
                            from. In the case of a folder, traverse recursively and retrieve documents.

            Returns a tuple containing the documents downloaded with highlights and all highlights commited to storage.
        """
        # pylint: disable=too-many-locals

        spinner = self._logger.spinner(text="Retrieving cloud metadata", spinner="bouncingBar")
        spinner.start()
        document_metadata = self._get_cloud_document_metadata(collection_names)
        stored_documents = self._storage.get_documents([doc.id for doc in document_metadata.values()])
        new_documents = _get_new_documents(document_metadata, stored_documents)
        changed_documents = _get_changed_documents(document_metadata, stored_documents)
        spinner.succeed()

        docs_to_filter = (new_documents + changed_documents)

        # Filter out documents whose parent is trash:

        docs_to_download = []
        for doc in docs_to_filter:
            if doc.parent is not None and doc.parent.lower() != "trash":
                docs_to_download.append(doc)

        self._download_documents(working_path, docs_to_download)

        extracted_highlights = []

        spinner = self._logger.spinner(text="Running extractors on documents", spinner="bouncingBar")
        spinner.start()
        for extractor in self._extractors:
            for doc in docs_to_download:
                spinner.text = f"Running extractor \"{extractor.__class__.__name__}\" on \"{doc.name}\""
                highlights = extractor.get_highlights(working_path, doc)
                extracted_highlights.extend(highlights)

        extracted_highlights_mapping = {
            highlight.hash: highlight for highlight in extracted_highlights
        }

        existing_highlights = self._storage.get_highlights(list(extracted_highlights_mapping.keys()))

        existing_highlights_mapping = {
            highlight.hash: highlight for highlight in existing_highlights
        }

        new_highlights = _get_new_highlights(existing_highlights_mapping, extracted_highlights_mapping)
        spinner.succeed(
            f"Ran extractors and found {len(extracted_highlights_mapping)} highlights, {len(new_highlights)} are new."
        )

        self._storage.save_models(new_documents)
        self._storage.update_documents(changed_documents)

        self._storage.save_models(new_highlights)
        self._storage.commit()

        highlights_by_doc_id = [highlight.document_id for highlight in new_highlights]

        docs_to_return = [doc for doc in docs_to_download if doc.id in highlights_by_doc_id]

        sorted_docs = sorted(docs_to_return, key=lambda doc: doc.name)
        document_lookup = {doc.id: doc for doc in sorted_docs}

        sorted_highlights = list(itertools.chain(*(
            sorted(group, key=lambda highlight: highlight.page_number)
            for key, group in
            itertools.groupby(
                sorted(new_highlights, key=lambda highlight: document_lookup[highlight.document_id].name),
                key=lambda highlight: document_lookup[highlight.document_id].name
            )
        )))

        return (sorted_docs, sorted_highlights)

    def _get_cloud_document_metadata(self, collection_names: List[str]) -> Dict[str, models.Document]:
        """
        Retrieve document metadata for collection names passed.

        If collection name is a folder, retrieve document data recursively.

        Returns a mapping of document id to models.Document
        """
        logging.info("Getting cloud document metadata")
        folder_objects = self._rmcloud.get_folders(collection_names)
        document_objects = self._rmcloud.get_documents(collection_names)

        document_objects_from_folders = self._rmcloud.crawl_folders(folder_objects)

        all_documents = document_objects_from_folders + document_objects

        documents = []
        for cloud_document in all_documents:
            documents.append(models.Document.from_cloud_document(cloud_document))

        document_rec: Dict[str, models.Document] = {}
        for doc in documents:
            document_rec[doc.id] = doc

        return document_rec

    def _download_documents(self, working_path: str, documents: List[models.Document]) -> None:
        """ Download the given documents to the given working_path """
        spinner = self._logger.spinner(text="Downloading documents", spinner="bouncingBar")
        spinner.start()
        for doc in documents:
            spinner.text = f"Downloading \"{doc.name}\""
            self._rmcloud.download_document(doc.id, working_path)
        spinner.succeed(f"Downloaded {len(documents)} documents.")


def _get_changed_documents(document_metadata:
                           Dict[str, models.Document],
                           stored_documents: List[models.Document]
                          ) -> List[models.Document]:
    """ Return a list of Document objects that represent the new current state of a document """
    document_rec_existing_changed = []
    logging.info("Getting changed documents")

    for doc_in_db in stored_documents:
        if doc_in_db.id is None:
            raise Exception("Found a document without an id")

        doc_possible_changed = document_metadata[doc_in_db.id]
        if doc_possible_changed.modified_client > doc_in_db.modified_client:
            # We know we have a new changes for the doc, let's add it the changed record so we can update it
            document_rec_existing_changed.append(doc_possible_changed)

    return document_rec_existing_changed


def _get_new_documents(document_metadata: Dict[str, models.Document],
                       stored_documents: List[models.Document]) -> List[models.Document]:
    """ Return a list of brand new documents by comparing retrieved document metadata to stored documents. """
    document_rec_new = []
    document_rec_existing_ids = [doc.id for doc in stored_documents]

    for doc_id, doc in document_metadata.items():
        if doc_id not in document_rec_existing_ids:
            document_rec_new.append(doc)

    return document_rec_new


def _get_new_highlights(existing_highlights: Dict[str, models.Highlight],
                        extracted_highlights: Dict[str, models.Highlight]) -> List[models.Highlight]:
    """ Compared existing highlights to extracted highlight to return brand new highlights"""
    new_highlights = []
    for key in extracted_highlights.keys():
        if key not in existing_highlights:
            new_highlights.append(extracted_highlights[key])
    return new_highlights
