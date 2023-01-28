from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


checkers_router = APIRouter()

templates = Jinja2Templates(directory='templates')

@checkers_router.get('/')
def home(request: Request):
    return templates.TemplateResponse('checkers/home.html', context={'request': request})

@checkers_router.get('/search')
def game_search(request: Request):
    return templates.TemplateResponse('checkers/gameSearch.html', context={'request': request})