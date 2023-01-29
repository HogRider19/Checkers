from fastapi import WebSocket


class GameController:
    
    def __init__(self) -> None:
        self._sessions = {
            'player_1': None,
            'player_2': None,
            'spectators': [],
        }

    def add_player(self, __session: WebSocket) -> None:
        if self._sessions['player_1'] is not None:
            self._sessions['player_1'] = __session
        elif self._sessions['player_2'] is not None:
            self._sessions['player_2'] = __session

    def add_spectators(self, __session: WebSocket) -> None:
        self._sessions['spectators'].append(__session)

    def send_message_everyone(self, __message: str) -> None:
        pass


        