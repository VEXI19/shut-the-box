from enums import ResponseStatus, ResponseType
from errors import GameError


class ServerResponseService:
    def __init__(self, send):
        self.send = send

    @staticmethod
    def __create_response(status, response_type, data):
        return {
            "status": status,
            "response_type": response_type,
            "data": data,
        }

    @staticmethod
    def __create_error_response(error_type, message):
        return {
            "status": ResponseStatus.ERROR,
            "error_type": error_type,
            "error_message": message
        }

    def create_session_response(self, session, client_socket):
        response = ServerResponseService.__create_response(ResponseStatus.SUCCESS, ResponseType.SESSION_CREATED, {
            "session_id": session.get_session_id(),
            "session_code": session.get_session_code()
        })
        self.send(client_socket, response)

    def join_session_response(self, session, client_socket):
        response = ServerResponseService.__create_response(ResponseStatus.SUCCESS, ResponseType.SESSION_JOINED, {
            "session_id": session.get_session_id(),
            "session_code": session.get_session_code()
        })
        self.send(client_socket, response)
        response = ServerResponseService.__create_response(ResponseStatus.SUCCESS, ResponseType.USER_JOINED, {
            "message": "User has joined the session"
        })
        for user_socket in session.get_user_sockets():
            if user_socket != client_socket:
                self.send(user_socket, response)

    def leave_session_response(self, session, client_socket):
        response = ServerResponseService.__create_response(ResponseStatus.SUCCESS, ResponseType.SESSION_LEFT, {
            "message": "You have left the session"
        })
        self.send(client_socket, response)
        if session:
            response = ServerResponseService.__create_response(ResponseStatus.SUCCESS, ResponseType.USER_LEFT, {
                "message": "User has left the session"
            })
            for user_socket in session.get_user_sockets():
                if user_socket != client_socket:
                    self.send(user_socket, response)

    def game_finished_response(self, game):
        player = game.get_current_player()
        response = ServerResponseService.__create_response(ResponseStatus.SUCCESS, ResponseType.GAME_ENDED, {
            "message": f"Player {player['name']} has won the game",
        })
        for user_socket in game.players:
            self.send(user_socket["socket"], response)

    def session_destroyed_response(self, session):
        response = ServerResponseService.__create_response(ResponseStatus.SUCCESS, ResponseType.SESSION_DESTROYED, {
            "message": "Session has been destroyed"
        })
        for user_socket in session.get_user_sockets():
            self.send(user_socket, response)

    def start_game_response(self, session):
        response = ServerResponseService.__create_response(ResponseStatus.SUCCESS, ResponseType.GAME_STARTED, {
            "message": "Game has started",
            "player_ids": session.game.get_players_ids()
        })
        current_player = session.game.get_current_player()
        if current_player is None:
            raise GameError("No current player found")

        for player in session.game.players:
            response["data"]["user_id"] = player["id"]
            response["data"]["current_turn_player_id"] = current_player["id"]
            print(response)
            self.send(player["socket"], response)

    def terminate_game_response(self, players):
        response = ServerResponseService.__create_response(ResponseStatus.SUCCESS, ResponseType.GAME_TERMINATED, {
            "message": "Game has been terminated due to lack of players"
        })
        for user_socket in players:
            self.send(user_socket["socket"], response)

    def roll_dice_response(self, roll_result, game):
        response = ServerResponseService.__create_response(ResponseStatus.SUCCESS, ResponseType.DICE_ROLLED, {
            "roll_result": roll_result,
            "board": game.get_current_player()["board"]
        })
        for user_socket in game.players:
            self.send(user_socket["socket"], response)

    def no_moves_response(self, game):
        response = ServerResponseService.__create_response(ResponseStatus.SUCCESS, ResponseType.NO_MOVES, {
            "message": "No moves available",
        })
        for user_socket in game.players:
            response["data"]["current_turn_player_id"] = game.get_current_player()["id"]
            self.send(user_socket["socket"], response)

    def player_eliminated_response(self, game, client_socket):
        player = game.get_player_by_socket(client_socket)
        response = ServerResponseService.__create_response(ResponseStatus.SUCCESS, ResponseType.PLAYER_ELIMINATED, {
            "message": f"Player {player['name']} has been eliminated",
        })
        for user_socket in game.players:
            response["data"]["current_turn_player_id"] = game.get_current_player()["id"]
            self.send(user_socket["socket"], response)

    def move_made_response(self, game, move):
        response = ServerResponseService.__create_response(ResponseStatus.SUCCESS, ResponseType.MOVE_MADE, {
            "message": f"Player has made a move",
            "move": move
        })
        for user_socket in game.players:
            self.send(user_socket["socket"], response)

    def server_error_response(self, client_socket, error_type, message):
        response = ServerResponseService.__create_error_response(error_type, message)
        self.send(client_socket, response)
