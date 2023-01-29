from fastapi import WebSocket
from string import ascii_lowercase


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
        self.send_message_players(__message)
        self.send_message_spectators(__message)

    def send_message_players(self, _message: str) -> None:
        pass

    def send_message_spectators(self, _message: str) -> None:
        pass


class CellOperationsMixin:

    def _parse_cell_position(self, pos: str) -> tuple[int, int]:
        return (int(pos[1])-1, ascii_lowercase.find(pos[0]))

    def _form_position_cell(self, x: int, y: int) -> str:
        return f"{ascii_lowercase[x]}{y+1}"

    def _get_displace_cell(self, pos: str, drow: int, dcol: int) -> str:
        r, c = self._parse_cell_position(pos)
        return self._form_position_cell(c+dcol, r+drow)
        


class CheckersGame(CellOperationsMixin):

    def __init__(self) -> None:
        self._board = Board(size=8)
        self._whose_move = 0

    def make_move(self, move_code: list[str]) -> bool:
        pass

    def _validate_move(self, move_code: list[str]) -> bool:
        from_ = move_code[0]
        to_ = move_code[1]
        is_valid = True

        allowed_cells = self._get_allowed_cells(from_)

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
        if is_valid:
            self._whose_move = 1 if self._whose_move == 0 else 0
        return is_valid
            
    def _get_allowed_cells(self, from_: str) -> list[str]:
        direct = 1 if self._whose_move == 0 else -1
        return [
            self._get_displace_cell(from_, direct, 1),
            self._get_displace_cell(from_, direct, -1),
            self._get_displace_cell(from_, 2 * direct, 2),
            self._get_displace_cell(from_, 2 * direct, -2),
        ]

    @property
    def whose_move(self) -> int:
        return self._whose_move


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
                        board[row_index][col_index] = 0
                    elif row_index >= size - 3:
                        board[row_index][col_index] = 1
        return board






