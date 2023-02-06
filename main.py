from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from auth.router import auth_router, register_router
from checkers.router_html import checkers_html_router
from checkers.router import checkers_router
from database.db import create_db_and_tables


from checkers.websockets import WebSocketControllerGroup
from uuid import uuid4

app = FastAPI(title='Checkers')

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

app.include_router(
    checkers_router,
    tags=["checkers"],
)

ws_group = WebSocketControllerGroup(limit=10)

@app.on_event('startup')
async def startup():
    ws_group.create_game("jawehgvjkwhaeejhroghkjewrg", 'Test Game', '1234')
    await create_db_and_tables()
