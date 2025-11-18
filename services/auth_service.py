from dataclasses import dataclass
from typing import Tuple

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from core.config import get_settings
from core.security import (
    TokenPair,
    create_token_pair,
    get_refresh_token_expiry,
    hash_refresh_token_value,
    verify_password,
)
from models import RefreshToken, User
from repositories.refresh_token_repository import RefreshTokenRepository
from repositories.user_repository import UserRepository


class AuthenticationError(Exception):
    pass


class RefreshTokenError(Exception):
    pass


@dataclass(frozen=True)
class AuthResult:
    user: User
    tokens: TokenPair


class AuthService:
    def __init__(
        self,
        session: Session,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ) -> None:
        self._session = session
        self._users = user_repository
        self._refresh_tokens = refresh_token_repository
        self._settings = get_settings()

    def authenticate(self, username: str, password: str) -> AuthResult:
        user = self._users.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid credentials")

        self._refresh_tokens.delete_expired()
        tokens = self._issue_new_tokens(user)
        self._session.commit()

        return AuthResult(user=user, tokens=tokens)

    def refresh(self, refresh_token: str) -> AuthResult:
        self._refresh_tokens.delete_expired()
        token_hash = hash_refresh_token_value(refresh_token)
        stored_token = self._refresh_tokens.get_by_hash(token_hash)
        if not stored_token or stored_token.revoked:
            raise RefreshTokenError("Invalid refresh token")

        stored_token.revoked = True
        user = stored_token.user
        if user is None:
            raise RefreshTokenError("Refresh token has no associated user")

        tokens = self._issue_new_tokens(user)
        self._session.commit()
        return AuthResult(user=user, tokens=tokens)

    def decode_access_token(self, token: str) -> Tuple[str, str]:
        try:
            payload = jwt.decode(
                token,
                self._settings.secret_key,
                algorithms=[self._settings.jwt_algorithm],
            )
        except JWTError as exc:
            raise AuthenticationError("Invalid access token") from exc

        token_type = payload.get("token_type")
        subject = payload.get("sub")
        if token_type != "access" or not subject:
            raise AuthenticationError("Invalid token payload")

        return subject, token_type

    def resolve_user_from_token(self, token: str) -> User:
        subject, _ = self.decode_access_token(token)
        user = self._users.get_by_username(subject)
        if not user:
            raise AuthenticationError("User not found")
        return user

    def _issue_new_tokens(self, user: User) -> TokenPair:
        tokens = create_token_pair(user.username)
        self._persist_refresh_token(tokens.refresh_token, user)
        return tokens

    def _persist_refresh_token(self, raw_refresh_token: str, user: User) -> None:
        refresh_entity = RefreshToken(
            token_hash=hash_refresh_token_value(raw_refresh_token),
            user_id=user.id,
            expires_at=get_refresh_token_expiry(),
            revoked=False,
        )
        self._refresh_tokens.create(refresh_entity)
        # session flush ensures id assigned before commit when needed elsewhere
        self._session.flush()
