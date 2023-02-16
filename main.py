from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from checkers.router import checkers_router
from checkers.router_html import checkers_html_router
from checkers.websockets import WebSocketControllerGroup


app = FastAPI(title='Checkers')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(
    checkers_html_router,
    tags=["html"],
)

app.include_router(
    checkers_router,
    tags=["checkers"],
)

ws_group = WebSocketControllerGroup(limit=30)

