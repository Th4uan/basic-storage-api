from fastapi import FastAPI

from api.routes.auth import router as auth_router
from api.routes.documents import router as documents_router
from api.routes.users import router as users_router
from core.config import get_settings
from database import Base, engine
import models  # noqa: F401 ensures metadata is loaded


Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(title=settings.app_name)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(users_router)
