import socket
import select
import threading
import time
import pickle

from errors import *
from dispatcher import Dispatcher
from session import SessionManager


class Server:
    HEADER_LENGTH = 10

    def __init__(self, host="127.0.0.1", port=12345):
        self.host = host
        self.port = port
        self.open_connections = []

        self.session_manager = SessionManager()
        self.dispatcher = Dispatcher(self.session_manager, self.send)

        # Create a non-blocking socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setblocking(False)  # Set socket to non-blocking mode

        # Bind and listen
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        Log.log(f"Server listening on {host}:{port}", Log.LogType.SERVER)

        self.open_connections.append(self.server_socket)

    def run(self):
        while True:
            # Use select to handle multiple connections
            readable, _, _ = select.select(self.open_connections, [], [])

            for sock in readable:
                if sock == self.server_socket:
                    # Accept new connection
                    client_socket, addr = self.server_socket.accept()
                    client_socket.setblocking(False)
                    self.open_connections.append(client_socket)
                    Log.log(f"New connection established", Log.LogType.INFO, client=client_socket)
                else:
                    # Receive data from client
                    try:
                        data_length_header = sock.recv(self.HEADER_LENGTH)
                        if data_length_header:
                            data_length = int(data_length_header.decode('utf-8').strip())
                            data_bytes = sock.recv(data_length)
                            if data_bytes:
                                message = pickle.loads(data_bytes)
                                Log.log(f"Message received", Log.LogType.INFO, client=sock)
                                print(f"Message: {message}")
                                self.dispatcher.dispatch(message, sock)
                        else:
                            # No data received, close the connection
                            Log.log(f"Connection terminated", Log.LogType.INFO, client=sock)
                            self.open_connections.remove(sock)
                            sock.close()
                    except socket.error as e:
                        # Handle socket errors
                        Log.log(f"Socket error", Log.LogType.ERROR, exception=e, client=sock)
                        self.open_connections.remove(sock)
                        Log.log(f"Connection terminated unexpectedly", Log.LogType.WARNING, client=sock)
                        sock.close()
                    except pickle.PickleError as e:
                        Log.log(f"Error deserializing data", Log.LogType.ERROR, exception=e, client=sock)

    def send(self, client_socket, data):
        data_bytes = pickle.dumps(data)
        data_length = len(data_bytes)
        header = f'{data_length:<{self.HEADER_LENGTH}}'.encode('utf-8')
        client_socket.sendall(header + data_bytes)
        Log.log("Data sent", Log.LogType.INFO, client=client_socket)

    def close(self):
        Log.log(f"Server closing", Log.LogType.SERVER)
        try:
            for sock in self.open_connections:
                Log.log(f"Connection terminated", Log.LogType.INFO, client=sock)
                sock.close()
        except Exception as e:
            Log.log(f"Error closing server", Log.LogType.ERROR, exception=e)
        finally:
            Log.log(f"Server closed", Log.LogType.SERVER)


def event_trigger(server_instance):
    while True:
        time.sleep(5)  # Simulate some event occurring every 5 seconds
        message = "Event occurred!"
        for sock in server_instance.open_connections[1:]:  # Skip the server socket
            server_instance.send(sock, message)


# Usage example:

# Start the non-blocking server
server = Server('localhost', 12345)
server_thread = threading.Thread(target=server.run)
server_thread.start()

# Start the event trigger in a separate thread
# event_thread = threading.Thread(target=event_trigger, args=(server,))
# event_thread.start()

# Wait for the server thread to complete (not necessary in production)
server_thread.join()

# Close the server gracefully
server.close()
