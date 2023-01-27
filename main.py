from fastapi import FastAPI
from database.db import create_db_and_tables
from auth.router import auth_router, register_router


app = FastAPI(title='Checkers')

app.include_router(
    auth_router,
    prefix="/auth/jwt",
    tags=["auth"])

app.include_router(
    register_router,
    prefix="/auth/jwt",
    tags=["auth"])

@app.on_event('startup')
async def startup():
    await create_db_and_tables()