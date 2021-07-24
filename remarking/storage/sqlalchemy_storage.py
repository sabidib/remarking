import typing as T
from typing import List, Sequence, Union

import sqlalchemy
from sqlalchemy import orm

from remarking import models as models_
from remarking.storage import storage as storage_


class SqlAlchemyStorage(storage_.Storage):
    """ Storage implmentation for SqlAlchemy """

    def __init__(self, db_string: str, echo: bool = False) -> None:
        self._engine = sqlalchemy.create_engine(db_string, echo=echo)
        self.echo = echo
        self._sessionmaker = orm.sessionmaker(bind=self._engine)
        models_.Base.metadata.create_all(self._engine)
        self._session = self._sessionmaker()

    def save_models(self, models: Sequence[Union[models_.Document,
                    models_.Highlight]]) -> None:
        self._session.bulk_save_objects(models)

    def update_documents(self, documents: List[models_.Document]) -> None:
        self._session.bulk_update_mappings(models_.Document, [doc.to_dict() for doc in documents])

    def get_documents(self, document_ids: T.Optional[List[str]] = None) -> List[models_.Document]:
        partial_query = self._session.query(models_.Document)
        if document_ids:
            partial_query = partial_query.filter(
                models_.Document.id.in_(document_ids))
        documents = partial_query.all()
        for document in documents:
            self._session.expunge(document)
        return documents

    def get_highlights(self, combined_text_hashes: T.Optional[List[str]] = None) -> List[models_.Highlight]:
        partial_query = self._session.query(models_.Highlight)
        if combined_text_hashes:
            partial_query = partial_query.filter(
                models_.Highlight.hash.in_(combined_text_hashes)
            )
        highlights = partial_query.all()
        for highlight in highlights:
            self._session.expunge(highlight)
        return highlights

    def commit(self) -> None:
        self._session.commit()
