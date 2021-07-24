import typing as T
from abc import ABCMeta, abstractmethod
from typing import List, Sequence, Union

from remarking import models as models_


class Storage(metaclass=ABCMeta):
    """ Storage interface

        All changes to storage should be committed only when commit is called.
    """

    @abstractmethod
    def get_documents(self, document_ids: T.Optional[List[str]] = None) -> List[models_.Document]:
        """ Return all documents with matching ID.
        If no IDs are passed, return all stored documents.
        """

    @abstractmethod
    def get_highlights(self, combined_text_hashes: List[str]) -> List[models_.Highlight]:
        """ Return all highlights with matching CombinedTextHashs.
        If no hashes are passed, return all stored highlights.
        """

    @abstractmethod
    def save_models(self, models: Sequence[Union[models_.Document, models_.Highlight]]) -> None:
        """ Save passed models into storage """

    @abstractmethod
    def update_documents(self, documents: List[models_.Document]) -> None:
        """ Update existing documents in the database.
        The passed models must already exist in storage.
        """

    @abstractmethod
    def commit(self) -> None:
        """ Commit changes to storage """


# TODO: This doesn't seem like a great idea? Then it means any time we use any storage
# we won't have any guarantees of something we store being there...
class NoStorage(Storage):
    """ Storage class that does not store anything.
    This is useful for cases where you need to pass a storage class but not actually store anything.
    """

    def get_documents(self, document_ids: T.Optional[List[str]] = None) -> List[models_.Document]:
        return []

    def get_highlights(self, combined_text_hashes: List[str]) -> List[models_.Highlight]:
        return []

    def save_models(self, models: Sequence[Union[models_.Document, models_.Highlight]]) -> None:
        pass

    def update_documents(self, documents: List[models_.Document]) -> None:
        pass

    def commit(self) -> None:
        pass
