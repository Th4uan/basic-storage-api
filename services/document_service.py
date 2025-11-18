import base64
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from models import Document
from repositories.document_repository import DocumentRepository


class DocumentNotFoundError(Exception):
    pass


class DocumentService:
    def __init__(self, session: Session, document_repository: DocumentRepository) -> None:
        self._session = session
        self._documents = document_repository

    async def save_upload(self, file: UploadFile, uri: str) -> Document:
        file_bytes = await file.read()
        document = Document(
            filename=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            uri=uri,
            base64_content=base64.b64encode(file_bytes).decode("utf-8"),
            file_bytes=file_bytes,
        )
        self._documents.add(document)
        self._session.commit()
        self._session.refresh(document)
        return document

    def get_document(self, document_id: int) -> Document:
        document: Optional[Document] = self._documents.get_by_id(document_id)
        if not document:
            raise DocumentNotFoundError(f"Document id={document_id} not found")
        return document
