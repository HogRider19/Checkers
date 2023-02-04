from uuid import uuid4
from loguru import logger

from fastapi import (APIRouter, Path, WebSocket, WebSocketDisconnect,
                    WebSocketException, Body, Query)

from checkers.utils import WebSocketControllerGroup, GameRsponseCode

checkers_router = APIRouter()
ws_group = WebSocketControllerGroup(limit=10)


@checkers_router.post('/game/create')
def create_game(
    name: str = Body(..., max_length=50),
    password: str = Body(default=None, max_length=8)
):
    id = uuid4()
    created = ws_group.create_game(str(id), name, password)
    return {'created': created, 'id': id}

@checkers_router.get('/game/list')
def get_games_list(
    page: int = Query(..., ge=0),
    page_size: int = Query(default=10, gt=0, le=100)
):
    lower = page * page_size
    upper = lower + page_size
    return ws_group.game_list()[lower:upper]


@checkers_router.websocket('/ws/{id}')
async def connect(ws: WebSocket, id: str = Path(...)) -> None:
    
    await ws.accept()

    logger.debug(f"ws_group = {ws_group._groups}")

    ws_controller = ws_group[id]

    logger.debug(f"ws_controller = {ws_controller}")

    if ws_controller is None:
        logger.debug("ws_controller is None")
        raise WebSocketException(code=1000, reason=f'Game with id:{id} does not exist')
    
    figure = ws_controller.add_player(ws)

    logger.debug(f"figure = {figure}")


    if figure is None:
        logger.debug("figure is None")
        raise WebSocketException(code=1001, reason='Game session is full')

    while True:
        try:
            await ws_controller.send_message_everyone(
                ws_controller.game.board._board)
            message = await ws.receive_text()
            code = ws_controller.make_move(ws, message)
        except WebSocketDisconnect:
            logger.debug("disconnect")
            ws_controller.disconnect(ws)
            # await ws.close()
            break


