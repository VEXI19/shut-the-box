from enums import ServerCommand, ResponseStatus, ResponseType, GameState
import pickle
from errors import ServerError


class ClientRequestService:
    def __init__(self, client_socket, send):
        self.client_socket = client_socket
        self.send = send

    def create_session_request(self):
        request = {
            "command": ServerCommand.CREATE_SESSION
        }
        self.send(request)

    def join_session_request(self, session_code):
        request = {
            "command": ServerCommand.JOIN_SESSION,
            "data": {
                "session_code": session_code
            }
        }
        self.send(request)

    def leave_session_request(self):
        request = {
            "command": ServerCommand.LEAVE_SESSION
        }
        self.send(request)

    def roll_dice_request(self):
        request = {
            "command": ServerCommand.ROLL_DICE
        }
        self.send(request)

    def make_move_request(self, move):
        request = {
            "command": ServerCommand.MAKE_MOVE,
            "data": {
                "move": move
            }
        }
        self.send(request)


class ClientReceiveService:
    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.message = None
        self.change_current_scene = None

    def receive(self, sock, data_length):
        data_bytes = sock.recv(data_length)
        if data_bytes:
            self.message = pickle.loads(data_bytes)
            if type(self.message) is not dict:
                raise ValueError("Received message is not a dictionary")
            if "status" not in self.message.keys():
                raise ValueError("Received message does not contain a status field")
            if self.message["status"] == ResponseStatus.ERROR:
                if "error_type" not in self.message.keys():
                    raise ValueError("Received message does not contain an error_type field")
                if "error_message" not in self.message.keys():
                    raise ValueError("Received message does not contain an error_message field")
                raise ServerError(f"Error: {self.message['error_type']}, {self.message['error_message']}")
            if self.message["status"] == ResponseStatus.SUCCESS:
                if "response_type" not in self.message.keys():
                    raise ValueError("Received message does not contain a response_type field")
                if "data" not in self.message.keys():
                    raise ValueError("Received message does not contain a data field")
                match self.message["response_type"]:
                    case ResponseType.SESSION_CREATED:
                        if "session_id" not in self.message["data"].keys():
                            raise ValueError("Received message does not contain a session_id field")
                        if "session_code" not in self.message["data"].keys():
                            raise ValueError("Received message does not contain a session_code field")
                        self.__session_created()
                    case ResponseType.SESSION_JOINED:
                        if "session_id" not in self.message["data"].keys():
                            raise ValueError("Received message does not contain a session_id field")
                        if "session_code" not in self.message["data"].keys():
                            raise ValueError("Received message does not contain a session_code field")
                        self.__session_joined()
                    case ResponseType.SESSION_LEFT:
                        self.__session_left()
                    case ResponseType.USER_JOINED:
                        self.__user_joined()
                    case ResponseType.USER_LEFT:
                        self.__user_left()
                    case ResponseType.GAME_STARTED:
                        self.__game_started()
                    case ResponseType.GAME_TERMINATED:
                        self.__game_terminated()
                    case ResponseType.DICE_ROLLED:
                        self.__dice_rolled()
                    case ResponseType.NO_MOVES:
                        self.__no_moves()
                    case ResponseType.PLAYER_ELIMINATED:
                        self.__player_eliminated()
                    case ResponseType.MOVE_MADE:
                        self.__move_made()
                    case ResponseType.GAME_ENDED:
                        self.__game_ended()
                    case ResponseType.SESSION_DESTROYED:
                        self.__session_destroyed()
                    case _:
                        raise ValueError("Received message contains an unknown response_type field")

    def __session_created(self):
        print(f"Session created.")
        print(f"Session code: {self.message['data']['session_code']}")

    def __session_joined(self):
        print(f"Session joined.")
        print(f"Session code: {self.message['data']['session_code']}")

    def __session_left(self):
        print(f"{self.message['data']['message']}")

    def __user_joined(self):
        print(f"{self.message['data']['message']}")

    def __user_left(self):
        print(f"{self.message['data']['message']}")

    def __game_started(self):
        print(f"Game started.")
        if self.message["data"]["current_turn_player_id"] == self.message["data"]["user_id"]:
            print("It is your turn")
        else:
            print(f"It is player {self.message['data']['current_turn_player_id']}'s turn")

    def __game_terminated(self):
        print(f"{self.message['data']['message']}")

    def __dice_rolled(self):
        print(f"Dice rolled: {self.message['data']['roll_result']}")
        print(f"Current board: {self.message['data']['board']}")

    def __no_moves(self):
        print(f"No moves available, current turn player id: {self.message['data']['current_turn_player_id']}")

    def __player_eliminated(self):
        print(self.message["data"])

    def __move_made(self):
        print(f"Move made, chosen numbers: {self.message['data']['move']}")

    def __game_ended(self):
        print(f"Game ended: {self.message['data']['message']}")

    def __session_destroyed(self):
        print(f"Session destroyed, you have been removed from the session")
