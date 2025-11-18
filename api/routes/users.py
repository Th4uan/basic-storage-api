from fastapi import APIRouter, Depends, HTTPException, status

from auth import get_user_service
from schemas import UserCreate, UserOut
from services.user_service import UserAlreadyExistsError, UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserOut:
    try:
        user = user_service.create_user(username=payload.username, password=payload.password)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return UserOut(id=user.id, username=user.username)
