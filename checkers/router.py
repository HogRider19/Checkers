from uuid import uuid4

from fastapi import (APIRouter, Path, WebSocket, WebSocketDisconnect,
                    WebSocketException)

from checkers.utils import WebSocketControllerGroup, GameRsponseCode

checkers_router = APIRouter()
ws_group = WebSocketControllerGroup(limit=10)


@checkers_router.websocket('/ws/{id}')
async def connect(ws: WebSocket, id: str = Path(...)) -> None:
    
    await ws.accept()

    ws_controller = ws_group[id]

    if ws_controller is None:
        raise WebSocketException(code=1000, reason=f'Game with id:{id} does not exist')
    
    ws_controller.add_player(ws)

    while True:
        try:
            message = await ws.receive_text()
            code = ws_controller.make_move(ws, message)
            await ws_controller.send_message_everyone(code)
        except WebSocketDisconnect:
            break


