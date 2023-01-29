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
        pass


class CheckersGame:

    def __init__(self) -> None:
        self._board = Board(size=8)


class Board:

    def __init__(self, size: int = 8) -> None:
        self._size = size
        self._board = self._generate_initial_state_board(size=size)
        self._cell_letters_map = {letter: index for index,
                                    letter in enumerate(ascii_lowercase)}

    def __getitem__(self, key: str) -> int | None:
        row_index, col_index = self._parse_cell_position(key)
        return self._board[row_index][col_index]

    def __setitem__(self, key, value) -> None:
        row_index, col_index = self._parse_cell_position(key)
        self._board[row_index][col_index] = value
    
    def __str__(self):
        st, letters_map = f"\n", {None: '   ', 0: ' w ', 1: ' b '}
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
            for col_index, cell in enumerate(row):
                if row_index % 2 == col_index % 2:
                    if row_index <= 2:
                        board[row_index][col_index] = 0
                    elif row_index >= size - 3:
                        board[row_index][col_index] = 1
        return board

    def _parse_cell_position(self, pos: str) -> tuple[int, int]:
        return (int(pos[1])-1, self._cell_letters_map[pos[0]])

b = Board(15)

b['h2'] = 1
b['f8'] = 0

print(b)