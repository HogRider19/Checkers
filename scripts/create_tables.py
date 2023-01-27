from database.db import engine


async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)