from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, token: RefreshToken) -> RefreshToken:
        self._session.add(token)
        return token

    def get_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        return (
            self._session.query(RefreshToken)
            .filter(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
            .first()
        )

    def revoke(self, token: RefreshToken) -> None:
        token.revoked = True

    def revoke_all_for_user(self, user_id: int) -> int:
        query = (
            self._session.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
        )
        updated = query.update({RefreshToken.revoked: True})
        return updated

    def delete_expired(self) -> int:
        query = self._session.query(RefreshToken).filter(
            RefreshToken.expires_at <= datetime.now(timezone.utc)
        )
        deleted = query.delete(synchronize_session=False)
        return deleted
