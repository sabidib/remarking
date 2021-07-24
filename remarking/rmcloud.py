""" RMCloud used for downloading and extracting from Remarkable Cloud """
import os
import typing as T
import zipfile
from typing import List

import rmapy
import rmapy.api as rmapi
from rmapy import collections as rmapy_collections
from rmapy import document as rmapy_document
from rmapy import folder as rmapy_folder


class RMCloudException(RuntimeError):
    """ Wrapper for Exceptions throw from RMCloud """


class AuthError(RMCloudException):
    """ Auth error with RMCloud """


class RenewAuthError(RMCloudException):
    """ Raised when renewing a token fails """


class RMCloud():
    """
    Download and extract documents from reMarkable cloud.
    """

    def __init__(self, auth_token: str):
        self._api_client = rmapi.Client()
        is_auth = self._api_client.is_auth()
        is_renewable = True
        renewable_exc = None

        try:
            self._api_client.renew_token()
        except rmapy.exceptions.AuthError as exc:
            renewable_exc = exc
            is_renewable = False

        if not is_auth and not is_renewable:
            try:
                self._api_client.register_device(auth_token)
            except rmapy.exceptions.AuthError as exc:
                raise AuthError() from exc
        elif not is_renewable:
            try:
                self._api_client.register_device(auth_token)
            except rmapy.exceptions.AuthError as exc:
                raise RenewAuthError() from renewable_exc

        self._api_client.renew_token()
        if not self._api_client.is_auth():
            raise AuthError()

    def get_meta_items(self) -> List[rmapy_collections.Collection]:
        """
        Fetch all meta items from the Remarkable Cloud.
        """
        return self._api_client.get_meta_items()

    def get_folders(self, folders: List[str] = None) -> List[rmapy_folder.Folder]:
        """
        Return folders matching the folder names passed.

        Return all folders by default.
        """
        items = self.get_meta_items()
        folder_items = [item for item in items if isinstance(item, rmapy_folder.Folder)]
        if folders is None:
            return folder_items

        lowered = [folder.lower() for folder in folders]
        return [folder for folder in folder_items if folder.VissibleName.lower() in lowered]

    def get_documents(self, documents: List[str] = None) -> List[rmapy_document.Document]:
        """
        Get documents matching the document names passed.

        Return all documents by default.
        """
        items = self.get_meta_items()
        document_items = [item for item in items if isinstance(item, rmapy_document.Document)]
        if documents is None:
            return document_items

        lowered = [document.lower() for document in documents]
        return [document for document in document_items if document.VissibleName.lower() in lowered]

    def crawl_folders(self, folders: List[rmapy_folder.Folder]) -> List[rmapy_document.Document]:
        """
        Recursively crawl a list of folders for all documents they contain.
        """
        items = self.get_meta_items()

        def _get_documents(
            docs_or_folders: T.Union[rmapy_document.Document, rmapy_folder.Folder]
        ) -> List[rmapy_document.Document]:
            documents = []
            for collection in docs_or_folders:
                if isinstance(collection, rmapy_document.Document):
                    documents.append(collection)
                elif isinstance(collection, rmapy_folder.Folder):
                    children = [item for item in items if item.Parent == collection.ID]
                    documents.extend(_get_documents(children))
            return documents
        return _get_documents(folders)

    def download_document(self, doc_id: str, path: str) -> None:
        """
        Download the document zip with the given doc id and expands it into the given path.

        Path is created if it does not exist
        """
        path_to_zip = os.path.join(path, doc_id + ".zip")
        os.makedirs(path, exist_ok=True)
        self._api_client.download(self._api_client.get_doc(doc_id)).dump(path_to_zip)

        with zipfile.ZipFile(path_to_zip, 'r') as zip_ref:
            zip_ref.extractall(path)
