from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


checkers_html_router = APIRouter()

templates = Jinja2Templates(directory='templates')


@checkers_html_router.get('/')
def home(request: Request):
    return templates.TemplateResponse('checkers/home.html', context={'request': request})

@checkers_html_router.get('/game/search')
def game_search(request: Request):
    return templates.TemplateResponse('checkers/gameSearch.html', context={'request': request})

@checkers_html_router.get('/game/create')
def game_create(request: Request):
    return templates.TemplateResponse('checkers/gameCreate.html', context={'request': request})

@checkers_html_router.get('/game/field/{id}')
def game_field(request: Request, id: str):
    return templates.TemplateResponse('checkers/gameField.html', context={'request': request})