from enum import Enum


class CustomEnum(Enum):
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


class ServerCommand(CustomEnum):
    CREATE_SESSION = "create_session"
    JOIN_SESSION = "join_session"
    LEAVE_SESSION = "leave_session"
    ROLL_DICE = "roll_dice"
    MAKE_MOVE = "make_move"


class ResponseStatus(CustomEnum):
    SUCCESS = "success"
    ERROR = "error"


class ResponseType(CustomEnum):
    SESSION_CREATED = "session_created"
    SESSION_JOINED = "session_joined"
    SESSION_LEFT = "session_left"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    GAME_STARTED = "game_started"
    GAME_TERMINATED = "game_terminated"
    DICE_ROLLED = "dice_rolled"
    NO_MOVES = "no_moves"
    PLAYER_ELIMINATED = "player_eliminated"
    MOVE_MADE = "move_made"
    GAME_ENDED = "game_ended"
    SESSION_DESTROYED = "session_destroyed"
