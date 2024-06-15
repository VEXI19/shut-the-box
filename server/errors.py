from log import Log


class ExceptionHandler:
    @staticmethod
    def handle_exception(e, server_response_service, client=None):
        if isinstance(e, SessionError):
            Log.log(f"Session error", Log.LogType.ERROR, exception=e, client=client)
            server_response_service.server_error_response(client, "SessionError", str(e))
        elif isinstance(e, BadRequestError):
            Log.log(f"Bad request error", Log.LogType.ERROR, exception=e, client=client)
            server_response_service.server_error_response(client, "BadRequestError", str(e))
        elif isinstance(e, GameError):
            Log.log(f"Game error", Log.LogType.ERROR, exception=e, client=client)
            server_response_service.server_error_response(client, "GameError", str(e))
        else:
            Log.log(f"Error", Log.LogType.ERROR, exception=e, client=client)
            server_response_service.server_error_response(client, "UnknownError", str(e))


class SessionError(Exception):
    pass


class BadRequestError(Exception):
    pass


class GameError(Exception):
    pass

