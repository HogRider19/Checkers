from enum import Enum
from string import ascii_lowercase

from fastapi import WebSocket
from typing import Callable
from functools import wraps


class Figure(Enum):
    WHITE: int = 0
    BLACK: int = 1


class GameRsponseCode(Enum):
    success: int = 0
    invalid_move: int = 1


def singleton(cls: Callable):
    instance = None

    @wraps(cls)
    def inner(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
        return instance

    return inner


class CellOperationsMixin:

    def _parse_cell_position(self, pos: str) -> tuple[int, int]:
        return (int(pos[1])-1, ascii_lowercase.find(pos[0]))

    def _form_position_cell(self, x: int, y: int) -> str:
        return f"{ascii_lowercase[x]}{y+1}"

    def _get_displace_cell(self, pos: str, drow: int, dcol: int) -> str:
        r, c = self._parse_cell_position(pos)
        return self._form_position_cell(c+dcol, r+drow)

class Board(CellOperationsMixin):

    def __init__(self, size: int = 8) -> None:
        self._size = size
        self._board = self._generate_initial_state_board(size=size)

    def __getitem__(self, key: str) -> int | None:
        row_index, col_index = self._parse_cell_position(key)
        return self._board[row_index][col_index]

    def __setitem__(self, key, value) -> None:
        row_index, col_index = self._parse_cell_position(key)
        self._board[row_index][col_index] = value

    def __repr__(self) -> str:
        st = ''
        for cell in sum(self._board, []):
            st += f"{cell if cell is not None else -1},"
        return st
    
    def __str__(self):
        st = f"\n"
        letters_map = {None: '   ', 0: ' w ', 1: ' b ', 2: 'W', 3: 'B'}
        for row_index, row in enumerate(self._board[::-1]):
            st += f'{self._size-row_index}'
            st += ' |' if self._size-row_index < 10 \
                            and self._size > 9 else '|'
            for cell in row:
                st += letters_map.get(cell)
            st += '\n'
        markup = ''.join([f" {l} " for l in ascii_lowercase[:self._size]])
        st += f"   {'_'*self._size*3}\n  "
        st += ' ' if self._size > 9 else ''
        st += f"{markup}\n"
        return st

    @staticmethod
    def _generate_initial_state_board(size: int = 8) -> list[list[int | None]]:
        board = [[None]*size for _ in range(size)]
        for row_index, row in enumerate(board):
            for col_index, _ in enumerate(row):
                if row_index % 2 == col_index % 2:
                    if row_index <= 2:
                        board[row_index][col_index] = Figure.WHITE.value
                    elif row_index >= size - 3:
                        board[row_index][col_index] = Figure.BLACK.value
        return board


class GameController(CellOperationsMixin):

    def __init__(self, name: str, password: str) -> None:
        self._name = name
        self._password = password
        self._board = Board(size=8)
        self._whose_move = 0

    def make_move(self, move_code: list[str]) -> GameRsponseCode:
        move = Move(move_code, self._whose_move, self._board)
        is_valid = move.is_valide()
        is_eating = move.is_eating()
        if is_valid:
            if is_eating:
                eating_cell = move.get_eating_cell()
                self._board[eating_cell] = None
            self._board[move._from] = None
            self._board[move._to] = self.whose_move
            self._whose_move = 1 if self._whose_move == 0 else 0
        if is_valid:
            return GameRsponseCode.success
        else:
            return GameRsponseCode.invalid_move

    @property
    def board(self) -> Board:
        return self._board

    @property
    def whose_move(self) -> int:
        return self._whose_move

    @property
    def name(self):
        return self._name

    @property
    def password(self):
        return self._password


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

    def disconnect(self, session: WebSocket) -> None:
        if session in self._sessions['spectators']:
            self._sessions['spectators'].remove(session)
        else:
            if self._sessions['player_1'] == session:
                self._sessions['player_1'] == None
            if self._sessions['player_2'] == session:
                self._sessions['player_2'] == None

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
    async def _send_message(session: WebSocket, message: str) -> None:
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


class Move(CellOperationsMixin):
    
    def __init__(self, move_code: list[str], whose_move: int, board: Board) -> None:
        self._whose_move = whose_move
        self._board = board
        self._from = move_code[0]
        self._to = move_code[1]

        self.__postinit__()

    def __postinit__(self) -> None:
        self._direct = 1 if self._whose_move == 0 else -1
        from_ri, from_ci = self._parse_cell_position(self._from)
        to_ri, to_ci = self._parse_cell_position(self._to)
        self._from_ri = from_ri
        self._from_ci = from_ci
        self._to_ri = to_ri
        self._to_ci = to_ci
        
    def is_valide(self) -> bool:
        from_ = self._from
        to_ = self._to
        is_valid = True

        allowed_cells = self._get_allowed_cells()

        if self._board[from_] is not self._whose_move:
            is_valid = False
        if to_ not in allowed_cells:
            is_valid = False
        if self._board[to_] is not None:
            is_valid = False
        if to_ == allowed_cells[2]:
            if self._board[allowed_cells[0]] == self._whose_move\
                    or self._board[allowed_cells[0]] is None:
                is_valid = False
        if to_ == allowed_cells[3]:
            if self._board[allowed_cells[1]] == self._whose_move\
                    or self._board[allowed_cells[1]] is None:
                is_valid = False
        return is_valid

    def is_eating(self) -> bool:
        if self._to in [
            self._get_displace_cell(self._from, 2 * self._direct, 2),
            self._get_displace_cell(self._from, 2 * self._direct, -2),
        ]:
            return True
        return False

    def get_eating_cell(self) -> None:
        return self._get_displace_cell(
            pos=self._from,
            drow=self._direct,
            dcol=1 if self._to_ci > self._from_ci else 0,
        )

    def _get_allowed_cells(self) -> list[str]:
        return [
            self._get_displace_cell(self._from, self._direct, 1),
            self._get_displace_cell(self._from, self._direct, -1),
            self._get_displace_cell(self._from, 2 * self._direct, 2),
            self._get_displace_cell(self._from, 2 * self._direct, -2),
        ]


if __name__ == '__main__':
    g = GameController
    while True:
        print(g._board)
        print(f"Player: {'White' if g.whose_move == 0 else 'Black'}")
        move_code = input("Move: ").split(' ')
        is_valid = g.make_move(move_code)
        if not is_valid:
            print("Invalid move!")







