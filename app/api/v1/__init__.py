from fastapi import APIRouter
from core.config import settings

from .auth import router as auth_router


api_router = APIRouter(prefix=settings.API_V1_STR)
api_router.include_router(auth_router)
