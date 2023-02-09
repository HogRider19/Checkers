from uuid import uuid4
from loguru import logger

from fastapi import (APIRouter, Path, WebSocket, WebSocketDisconnect,
                     WebSocketException, Body, Query)

from checkers.enums import GameRsponseCode, ServerMessageType, ClientMessageType, Figure
from checkers.websockets import WebSocketControllerGroup, serialize_client_message

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
        raise WebSocketException(
            code=1000, reason=f'Game with id:{id} does not exist')

    figure = ws_controller.add_player(ws)

    logger.debug(f"figure = {figure}")

    if figure is None:
        logger.debug("figure is None")
        raise WebSocketException(code=1001, reason='Game session is full')

    while True:
        try:

            response = await ws.receive_text()

            message = serialize_client_message(response)

            if message is None:
                await ws_controller.send_message(ws, {
                    'type': ServerMessageType.InvalidRequest.value,
                })

            elif message.get('type') == ClientMessageType.GetMyFigureType:
                await ws_controller.send_message(ws, {
                    'type': ServerMessageType.FigureType.value,
                    'message': ws_controller.get_figure_type(ws).value,
                })

            elif message.get('type') == ClientMessageType.GetBoard:
                await ws_controller.send_message(ws, {
                    'type': ServerMessageType.Board.value,
                    'message': ws_controller.game.board.data,
                })

            elif message.get('type') == ClientMessageType.MakeMove:
                figure = ws_controller.get_figure_type(ws)
                whose_move = ws_controller.game.whose_move
                if whose_move != figure:
                    await ws_controller.send_message(ws, {
                        'type': ServerMessageType.NotYourMove.value})
                    continue
                
                move_result = ws_controller.make_move(ws, message.get('message'))

                if move_result == GameRsponseCode.success:
                    await ws_controller.send_message_everyone({
                        'type': ServerMessageType.Board.value,
                        'message': ws_controller.game.board.data,
                    })
                else:
                    await ws_controller.send_message(ws, {
                        'type': ServerMessageType.InvalidMove.value})

        except WebSocketDisconnect:
            logger.debug("disconnect")
            ws_controller.disconnect(ws)
            break
