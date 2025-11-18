from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import SessionLocal
from repositories.document_repository import DocumentRepository
from repositories.refresh_token_repository import RefreshTokenRepository
from repositories.user_repository import UserRepository
from services.auth_service import AuthService, AuthenticationError
from services.document_service import DocumentService
from services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(
        session=db,
        user_repository=UserRepository(db),
        refresh_token_repository=RefreshTokenRepository(db),
    )


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(session=db, document_repository=DocumentRepository(db))


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(session=db, user_repository=UserRepository(db))


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        return auth_service.resolve_user_from_token(token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
