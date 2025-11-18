from typing import Optional

from sqlalchemy.orm import Session

from models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_username(self, username: str) -> Optional[User]:
        return self._session.query(User).filter(User.username == username).first()

    def add(self, user: User) -> User:
        self._session.add(user)
        return user
