from warnings import *
from datetime import datetime
from enum import Enum
import uuid
from enums import ServerCommand
import traceback
import threading

print("hello  world")

def loop():
    while True:
        pass

thread = threading.Thread(target=loop)
thread.start()

print("hello")
