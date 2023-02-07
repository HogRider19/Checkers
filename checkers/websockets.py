from fastapi import WebSocket
from typing import Any
from checkers.game import GameController
from checkers.utils import singleton
from checkers.enums import Figure, GameRsponseCode
from checkers.enums import ClientMessageType, ServerMessageType

import json
from json import JSONDecodeError


def serialize_client_message(
    message: dict) -> dict[ClientMessageType, Any] | None:
    try:
        data = json.loads(message)
    except JSONDecodeError:
        return None
    
    if isinstance(data, dict) and 'type' in data:

        if isinstance(data['type'], int):

            try:
                data['type'] = ClientMessageType(data['type'])
                return data
            except ValueError:
                return None


def serialize_server_message(type: ServerMessageType, message: Any) -> str:
    data = None
    if type == ServerMessageType.Board:
        data = {'type': type.value, 'message': message}

    if type == ServerMessageType.FigureType:
        data = {'type': type.value, 'message': message}

    return data

class WebsocketController:
    
    def __init__(self, name: str, password: str) -> None:
        self._game = GameController(name, password)
        self._sessions = {
            'player_1': None,
            'player_2': None,
            'spectators': [],
        }

    def add_player(self, session: WebSocket) -> Figure:
        if self._sessions['player_1'] is None:
            self._sessions['player_1'] = session
            return Figure.WHITE.value
        elif self._sessions['player_2'] is None:
            self._sessions['player_2'] = session
            return Figure.BLACK.value

    def add_spectators(self, session: WebSocket) -> None:
        self._sessions['spectators'].append(session)

    def make_move(self, session: WebSocket, raw_comand: str) -> GameRsponseCode:
        comand = raw_comand.split(' ')[:2]
        return self._game.make_move(comand)

    def get_figure_type(self, session: WebSocket) -> Figure:
        if self._sessions['player_1'] == session:
            return Figure.WHITE
        elif self._sessions['player_2'] == session:
            return Figure.BLACK
        else:
            return Figure.SPECTATOR

    def disconnect(self, session: WebSocket) -> None:
        if session in self._sessions['spectators']:
            self._sessions['spectators'].remove(session)
        else:
            if self._sessions['player_1'] == session:
                self._sessions['player_1'] = None
            if self._sessions['player_2'] == session:
                self._sessions['player_2'] = None

    async def send_message_everyone(self, message: str) -> None:
        await self.send_message_players(message)
        await self.send_message_spectators(message)

    async def send_message_players(self, message: str) -> None:
        if self._sessions['player_1'] is not None:
            await self._send_message(self._sessions['player_1'], message)
        if self._sessions['player_2'] is not None:
            await self._send_message(self._sessions['player_2'], message)

    async def send_message_spectators(self, message: str) -> None:
        for sp in self._sessions.get('spectators'):
            await self._send_message(sp, message)

    @staticmethod
    async def send_message(session: WebSocket, message: str) -> None:
        await session.send_json(message)

    @property
    def game(self) -> GameController:
        return self._game

    @property
    def name(self):
        return self._game.name

    @property
    def password(self):
        return self._game.password

@singleton
class WebSocketControllerGroup:
    
    def __init__(self, limit: int) -> None:
        self._groups: dict[str, WebsocketController] = {}
        self._limit = limit

    def __getitem__(self, id: str) -> WebsocketController | None:
        return self._groups.get(id)

    def game_list(self) -> list[str, str]:
        return [[self._groups[id].name, id] for id in self._groups]

    def create_game(self, id: str, name: str, password: str) -> bool:
        created = False
        if len(self._groups) <= self._limit:
            self._groups.update({id: WebsocketController(name, password)})
            created = True
        return created

    def delete_game(self, id: str) -> None:
        del self._groups[id]