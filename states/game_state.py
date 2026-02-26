from enum import Enum

class GameState(Enum):
    WAITING = "waiting"
    STARTING = "starting"
    NIGHT = "night"
    DAY = "day"
    VOTING = "voting"
    ENDED = "ended"
