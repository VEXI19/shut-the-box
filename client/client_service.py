from enums import ServerCommand, ResponseStatus, ResponseType
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
                    case _:
                        raise ValueError("Received message contains an unknown response_type field")

    def __session_created(self):
        print(self.message["data"])

    def __session_joined(self):
        print(self.message["data"])

    def __session_left(self):
        print(self.message["data"])

    def __user_joined(self):
        print(self.message["data"])

    def __user_left(self):
        print(self.message["data"])

    def __game_started(self):
        print(self.message["data"])

    def __game_terminated(self):
        print(self.message["data"])

    def __dice_rolled(self):
        print(self.message["data"])

    def __no_moves(self):
        print(self.message["data"])

    def __player_eliminated(self):
        print(self.message["data"])

    def __move_made(self):
        print(self.message["data"])

