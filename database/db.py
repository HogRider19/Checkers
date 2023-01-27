from sqlalchemy.orm import declarative_base, DeclarativeMeta, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import AsyncGenerator

from config.config import (DB_DRIVER, DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT,
                           DB_USER)


DATABASE_URL = f"postgresql+{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL)
Base: DeclarativeMeta = declarative_base(bind=engine)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
