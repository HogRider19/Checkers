import uuid

from fastapi_users import FastAPIUsers

from auth.backend import auth_backend
from auth.depends import get_user_manager
from auth.models import User

from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import UserRead, UserCreate

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend])

auth_router = fastapi_users.get_auth_router(auth_backend)
register_router = fastapi_users.get_register_router(UserRead, UserCreate)

    