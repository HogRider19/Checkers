import json
import re
from json import JSONDecodeError
from typing import Any

from fastapi import WebSocket

from checkers.enums import ClientMessageType, Figure, GameRsponseCode
from checkers.game import GameController
from checkers.utils import singleton


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


class WebsocketController:

    def __init__(self, name: str, password: str) -> None:
        self._game = GameController(name, password)
        self._sessions = {
            'player_1': None,
            'player_2': None,
            'spectators': [],
        }

    def add_player(self, session: WebSocket) -> Figure | None:
        if self._sessions['player_1'] is None:
            self._sessions['player_1'] = session
            return Figure.WHITE.value
        elif self._sessions['player_2'] is None:
            self._sessions['player_2'] = session
            return Figure.BLACK.value

    def make_move(self, session: WebSocket, raw_comand: str) -> GameRsponseCode:
        comand = re.findall(r'[a-h][1-8]', str(raw_comand))
        if len(comand) == 2:
            return self._game.make_move(comand)
        else:
            return GameRsponseCode.invalid_move

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

    def finish(self):
        if self._sessions['player_1'] is not None:
            self._sessions['player_1'].close()
        if self._sessions['player_2'] is not None:
            self._sessions['player_2'].close()

    async def send_message_everyone(self, message: str) -> None:
        await self.send_message_players(message)
        await self.send_message_spectators(message)

    async def send_message_players(self, message: str) -> None:
        if self._sessions['player_1'] is not None:
            await self.send_message(self._sessions['player_1'], message)
        if self._sessions['player_2'] is not None:
            await self.send_message(self._sessions['player_2'], message)

    async def send_message_spectators(self, message: str) -> None:
        for sp in self._sessions.get('spectators'):
            await self.send_message(sp, message)

    @staticmethod
    async def send_message(session: WebSocket, message: str) -> None:
        await session.send_json(message)

    @property
    def game(self) -> GameController:
        return self._game

    @property
    def enemy(self, current_ws: WebSocket) -> WebSocket:
        if current_ws == self._sessions['player_1']:
            return self._sessions['player_2']
        return self._sessions['player_1']

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

    def delete_game(self, controller: WebsocketController) -> None:
        del self._groups[controller]

    def delete_game(self, id: str) -> None:
        del self._groups[id]
