from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from auth import get_current_user, get_document_service
from models import User
from schemas import DocumentOut
from services.document_service import DocumentNotFoundError, DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    uri: str = Form(...),
    document_service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
) -> DocumentOut:
    document = await document_service.save_upload(file=file, uri=uri)
    return document


@router.get("/{document_id}")
def download_document(
    document_id: int,
    document_service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
):
    try:
        document = document_service.get_document(document_id=document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return StreamingResponse(
        BytesIO(document.file_bytes),
        media_type=document.mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{document.filename}"'
        },
    )
