import datetime
import uuid

from fastapi_users import schemas as fastapi_users_schemas


class UserRead(fastapi_users_schemas.BaseUser[uuid.UUID]):
    username: str


class UserCreate(fastapi_users_schemas.BaseUserCreate):
    username: str


class UserUpdate(fastapi_users_schemas.BaseUserUpdate):
    pass