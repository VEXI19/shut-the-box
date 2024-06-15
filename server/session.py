import uuid
from errors import SessionError
from game import Game


class Session:
    USER_LIMIT = 2

    def __init__(self, user_socket):
        self.session_id = uuid.uuid4()
        self.user_sockets = [user_socket]
        self.session_code = str(uuid.uuid4().int)[:6]
        self.game = Game(self.USER_LIMIT)

    def start_game(self):
        self.game.start(self.user_sockets)

    def get_session_id(self):
        return self.session_id.int

    def get_user_sockets(self):
        return self.user_sockets

    def get_user_count(self):
        return len(self.user_sockets)

    def get_session_code(self):
        return self.session_code

    def add_user_socket(self, user_socket):
        if len(self.user_sockets) >= self.USER_LIMIT:
            raise SessionError("Session is full")
        self.user_sockets.append(user_socket)

    def remove_user_socket(self, user_socket):
        self.user_sockets.remove(user_socket)


class SessionManager:
    def __init__(self):
        self.sessions = []

    def create_session(self, user_socket):
        if self.get_session_by_user_socket(user_socket):
            raise SessionError("User is already part of a session")
        session = Session(user_socket)
        self.sessions.append(session)
        return session

    def join_session(self, session_code, user_socket):
        if self.get_session_by_user_socket(user_socket):
            raise SessionError("User is already part of a session")

        session = self.__get_session_by_code(session_code)
        if session:
            session.add_user_socket(user_socket)
            return session
        raise SessionError(f"Session with code {session_code} does not exist")

    def leave_session(self, user_socket):
        session = self.get_session_by_user_socket(user_socket)
        if session:
            if session.game.game_live and session.game.get_player_by_socket(user_socket) is not None:
                session.game.remove_player(user_socket)
            session.remove_user_socket(user_socket)
            if len(session.get_user_sockets()) == 0:
                self.__remove_session(session.get_session_id())
                return None
            return session
        raise SessionError("User is not part of any session")

    def delete_session(self, session_id):
        if self.__remove_session(session_id):
            return True
        raise SessionError(f"Session with id {session_id} does not exist")

    def __get_session(self, session_id):
        for session in self.sessions:
            if session.session_id == session_id:
                return session
        return None

    def __remove_session(self, session_id):
        for session in self.sessions:
            if session.session_id == session_id:
                self.sessions.remove(session)
                return True
        return False

    def __get_all_sessions(self):
        return self.sessions

    def get_session_by_user_socket(self, user_socket):
        for session in self.sessions:
            if user_socket in session.get_user_sockets():
                return session
        return None

    def __get_session_by_code(self, session_code):
        for session in self.sessions:
            if session.get_session_code() == session_code:
                return session
        return None