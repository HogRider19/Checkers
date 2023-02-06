from enum import Enum


class Figure(Enum):
    WHITE: int = 0
    BLACK: int = 1


class GameRsponseCode(Enum):
    success: int = 0
    invalid_move: int = 1


class ClientMessageType(Enum):
    GetMyFigureType: int = 0
    GetBoard: int = 1
    MakeMove: int = 2
    