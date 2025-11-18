from sqlalchemy.orm import Session

from core.security import hash_password
from models import User
from repositories.user_repository import UserRepository


class UserAlreadyExistsError(Exception):
    pass


class UserService:
    def __init__(self, session: Session, user_repository: UserRepository) -> None:
        self._session = session
        self._users = user_repository

    def create_user(self, username: str, password: str) -> User:
        existing = self._users.get_by_username(username)
        if existing:
            raise UserAlreadyExistsError("Username is already in use")

        user = User(username=username, password_hash=hash_password(password))
        self._users.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user
