from errors import *
from enums import ServerCommand
from server_response_service import ServerResponseService


class Dispatcher:
    def __init__(self, session_manager, send):
        self.session_manager = session_manager
        self.server_response_service = ServerResponseService(send)

    def dispatch(self, message, client_socket):
        try:
            if type(message) is not dict:
                raise BadRequestError("Request has to be a dictionary")
            if type(message) is not dict and "command" not in message.keys():
                raise BadRequestError("Request does not contain a command field")

            match message["command"]:
                case ServerCommand.CREATE_SESSION:
                    session = self.session_manager.create_session(client_socket)
                    self.server_response_service.create_session_response(session, client_socket)
                case ServerCommand.JOIN_SESSION:
                    if type(message) is not dict and "data" not in message.keys():
                        raise BadRequestError("Request does not contain a data field")
                    if "session_code" not in message["data"].keys():
                        raise BadRequestError("Data field does not contain a session_code field")

                    session = self.session_manager.join_session(message["data"]["session_code"], client_socket)
                    self.server_response_service.join_session_response(session, client_socket)

                    if session.get_user_count() == session.USER_LIMIT:
                        session.start_game()
                        self.server_response_service.start_game_response(session)

                case ServerCommand.LEAVE_SESSION:
                    session = self.session_manager.leave_session(client_socket)
                    self.server_response_service.leave_session_response(session, client_socket)

                    if session.game.get_player_count() == 1:
                        players = session.game.terminate()
                        self.server_response_service.terminate_game_response(players)

                case ServerCommand.ROLL_DICE:
                    game = self.session_manager.get_session_by_user_socket(client_socket).game
                    if not game.game_live:
                        raise GameError("Game is not live")
                    if game.get_player_by_socket(client_socket) is None:
                        raise GameError("User is not part of the game")
                    if game.get_current_player()["socket"] != client_socket:
                        raise GameError("It is not your turn")
                    roll_result = game.roll_dice()
                    self.server_response_service.roll_dice_response(roll_result, game)
                    is_move_possible = game.check_if_move_possible(roll_result)
                    if not is_move_possible:
                        game.next_player_turn()
                        self.server_response_service.no_moves_response(game)

                case ServerCommand.MAKE_MOVE:
                    game = self.session_manager.get_session_by_user_socket(client_socket).game
                    if type(message) is not dict and "data" not in message.keys():
                        raise BadRequestError("Request does not contain a data field")
                    if "move" not in message["data"].keys():
                        raise BadRequestError("Data field does not contain a move field")
                    if not game.game_live:
                        raise GameError("Game is not live")
                    if game.get_player_by_socket(client_socket) is None:
                        raise GameError("User is not part of the game")
                    if game.get_current_player()["socket"] != client_socket:
                        raise GameError("It is not your turn")
                    move = message["data"]["move"]
                    is_board_empty = game.make_move(move)
                    self.server_response_service.move_made_response(game, move)
                    if is_board_empty:
                        game.end()
                        self.server_response_service.game_finished_response(game)
                        session = self.session_manager.get_session_by_user_socket(client_socket)
                        self.server_response_service.session_destroyed_response(session)
                        self.session_manager.delete_session(session.get_session_id())

                case _:
                    raise BadRequestError("Provided command is not valid")
        except Exception as e:
            ExceptionHandler.handle_exception(e, self.server_response_service, client_socket)

