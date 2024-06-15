import datetime
import os
from enum import Enum
import traceback


class Log:
    __path = None

    class __LogColor(Enum):
        INFO = '\033[94m'
        ERROR = '\033[91m'
        WARNING = '\033[93m'
        SERVER = '\033[92m'
        ENDC = '\033[0m'

    class LogType(Enum):
        INFO = "INFO"
        ERROR = "ERROR"
        WARNING = "WARNING"
        SERVER = "SERVER"

    @staticmethod
    def __get_time(for_file_name=False):
        now = datetime.datetime.now()
        if for_file_name:
            return now.strftime('%Y-%m-%d_%H-%M-%S')
        return now.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def __create_file():
        if not os.path.exists('logs'):
            os.makedirs('logs')
        Log.__path = f"./logs/{Log.__get_time(True)}_0.log"
        index = 0
        while os.path.exists(f"./logs/{Log.__get_time(True)}_{index}.txt"):
            Log.__path = f"./logs/{Log.__get_time(True)}_{index}.txt"
            index += 1

    @staticmethod
    def construct_message(message, e, client, log_type):
        if e is not None:
            message = f"{message}: {e}"
        if client is not None:
            return f"[{Log.__get_time()}] [{log_type.value}] <{client.getpeername()[0]}:{client.getpeername()[1]}> {message}"
        return f"[{Log.__get_time()}] [{log_type.value}] {message}"

    @staticmethod
    def print_colored(message, log_type):
        match log_type:
            case Log.LogType.INFO:
                print(f"{Log.__LogColor.INFO.value}{message}{Log.__LogColor.ENDC.value}")
            case Log.LogType.WARNING:
                print(f"{Log.__LogColor.WARNING.value}{message}{Log.__LogColor.ENDC.value}")
            case Log.LogType.ERROR:
                print(f"{Log.__LogColor.ERROR.value}{message}{Log.__LogColor.ENDC.value}")
            case Log.LogType.SERVER:
                print(f"{Log.__LogColor.SERVER.value}{message}{Log.__LogColor.ENDC.value}")

    @staticmethod
    def __write(message):
        if Log.__path is None:
            Log.__create_file()
        with open(Log.__path, 'a') as f:
            f.write(f"[{Log.__get_time()}] {message}\n")

    @staticmethod
    def log(message, log_type, exception=None, client=None, verbose=True):
        message = Log.construct_message(message, exception, client, log_type)
        Log.__write(message)

        if exception is not None:
            tb_str = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            Log.print_colored(tb_str, log_type)
        elif verbose:
            Log.print_colored(message, log_type)

    #
    # @staticmethod
    # def add_error_log(message, client=None, verbose=True):
    #     message = Log.construct_message(message, client, Log.__LogType.ERROR)
    #     Log.__write(message)
    #
    #     if verbose:
    #         Log.print_colored(message, Log.__LogColor.ERROR)
    #
    # @staticmethod
    # def add_warning_log(message, client=None, verbose=True):
    #     message = Log.construct_message(message, client, Log.__LogType.WARNING)
    #     Log.__write(message)
    #
    #     if verbose:
    #         Log.print_colored(message, Log.__LogColor.WARNING)
    #
    # @staticmethod
    # def add_info_log(message, client=None, verbose=True):
    #     message = Log.construct_message(message, client, Log.__LogType.INFO)
    #     Log.__write(message)
    #
    #     if verbose:
    #         Log.print_colored(message, Log.__LogColor.INFO)
    #
    # @staticmethod
    # def add_server_log(message, client=None, verbose=True):
    #     message = Log.construct_message(message, client, Log.__LogType.SERVER)
    #     Log.__write(message)
    #
    #     if verbose:
    #         Log.print_colored(message, Log.__LogColor.SERVER)
