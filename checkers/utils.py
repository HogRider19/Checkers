from fastapi import WebSocket
from string import ascii_lowercase
from enum import Enum


class Figure(Enum):
    WHITE: int = 0
    BLACK: int = 1

class GameRsponseCode(Enum):
    success: int = 0
    invalid_move: int = 1

class GameController:
    
    def __init__(self) -> None:
        self._sessions = {
            'player_1': None,
            'player_2': None,
            'spectators': [],
        }

    def add_player(self, session: WebSocket) -> None:
        if self._sessions['player_1'] is not None:
            self._sessions['player_1'] = session
        elif self._sessions['player_2'] is not None:
            self._sessions['player_2'] = session

    def add_spectators(self, session: WebSocket) -> None:
        self._sessions['spectators'].append(session)

    def send_message_everyone(self, message: str) -> None:
        self.send_message_players(message)
        self.send_message_spectators(message)

    def send_message_players(self, message: str) -> None:
        pass

    def send_message_spectators(self, message: str) -> None:
        pass

    @staticmethod
    async def _send_message(session: WebSocket, command: str) -> None:
        await session.send_json(command)


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


class CheckersGame(CellOperationsMixin):

    def __init__(self) -> None:
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
        return is_valid

    @property
    def whose_move(self) -> int:
        return self._whose_move


g = CheckersGame()
while True:
    print(g._board)
    print(f"Player: {'White' if g.whose_move == 0 else 'Black'}")
    move_code = input("Move: ").split(' ')
    is_valid = g.make_move(move_code)
    if not is_valid:
        print("Invalid move!")







