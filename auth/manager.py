import uuid

from fastapi import Depends
from fastapi_users import (BaseUserManager, InvalidPasswordException,
                           UUIDIDMixin)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from config.config import SECRET
from database.db import get_async_session


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def validate_password(self, password: str, user: User) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters")
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail")

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
