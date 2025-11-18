from typing import Optional

from sqlalchemy.orm import Session

from models import Document


class DocumentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, document: Document) -> Document:
        self._session.add(document)
        return document

    def get_by_id(self, document_id: int) -> Optional[Document]:
        return self._session.query(Document).filter(Document.id == document_id).first()
