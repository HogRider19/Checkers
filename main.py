from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from auth.router import auth_router, register_router
from checkers.router_html import checkers_html_router
from database.db import create_db_and_tables


app = FastAPI(title='Checkers')

app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(
    auth_router,
    prefix="/auth/jwt",
    tags=["auth"])

app.include_router(
    register_router,
    prefix="/auth/jwt",
    tags=["auth"])

app.include_router(
    checkers_html_router,
    tags=["html"],
)

@app.on_event('startup')
async def startup():
    await create_db_and_tables()
