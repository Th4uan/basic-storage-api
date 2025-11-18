import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt
from passlib.context import CryptContext

from core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


def hash_password(raw_password: str) -> str:
    return pwd_context.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(raw_password, hashed_password)


def _build_access_payload(subject: str, *, expires_delta: timedelta) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    expire_at = now + expires_delta
    return {
        "sub": subject,
        "token_type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire_at.timestamp()),
    }


def _encode_token(payload: Dict[str, Any]) -> str:
    settings = get_settings()
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expires = timedelta(minutes=settings.access_token_exp_minutes)
    payload = _build_access_payload(subject, expires_delta=expires)
    return _encode_token(payload)


def generate_refresh_token_value() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token_value(raw_value: str) -> str:
    return hashlib.sha256(raw_value.encode("utf-8")).hexdigest()


def get_refresh_token_expiry() -> datetime:
    settings = get_settings()
    return datetime.now(timezone.utc) + timedelta(minutes=settings.refresh_token_exp_minutes)


def create_token_pair(subject: str) -> TokenPair:
    access_token = create_access_token(subject)
    refresh_token = generate_refresh_token_value()
    return TokenPair(access_token=access_token, refresh_token=refresh_token)
