from enum import Enum

class Gamemodes(Enum):
    CLASSIC = 1
    REVERSED = 2
    HARDCORE = 3
    
class Difficulty(Enum):
    EASY = 1
    NORMAL = 2
    HARD = 3
    
class RoomStatus(Enum):
    WAITING = 1
    PLAYING = 2