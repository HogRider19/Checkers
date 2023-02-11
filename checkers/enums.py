from enum import Enum


class Figure(Enum):
    WHITE: int = 0
    BLACK: int = 1
    SPECTATOR: int = 3


class GameRsponseCode(Enum):
    success: int = 0
    invalid_move: int = 1


class ClientMessageType(Enum):
    GetMyFigureType: int = 0
    GetBoard: int = 1
    MakeMove: int = 2
    Surrender: int = 3


class ServerMessageType(Enum):
    FigureType: int = 0
    Board: int = 1
    MoveResponse: int = 2
    InvalidRequest: int = 3
    NotYourMove: int = 4
    InvalidMove: int = 5
    Winner: int = 6
    