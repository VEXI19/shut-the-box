import os
import socket
import threading

import select
import pickle
from client_service import ClientRequestService, ClientReceiveService
from enums import GameState
from errors import ServerError


class Client:
    HEADER_LENGTH = 10

    def __init__(self, host="127.0.0.1", port=12345):
        self.host = host
        self.port = port

        # Create a non-blocking socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setblocking(False)  # Set socket to non-blocking mode

        self.client_request_service = ClientRequestService(self.client_socket, self.send)
        self.client_receive_service = ClientReceiveService(self.client_socket)

        try:
            self.client_socket.connect((self.host, self.port))
        except BlockingIOError:
            pass  # Continue execution if connection is in progress

        self.inputs = [self.client_socket]

    def receive(self):
        while self.inputs:
            readable, _, _ = select.select(self.inputs, [], [])

            for sock in readable:
                if sock == self.client_socket:
                    # Handle incoming data or errors from the server
                    try:
                        data_length_header = sock.recv(self.HEADER_LENGTH)
                        if data_length_header:
                            data_length = int(data_length_header.decode('utf-8').strip())
                            self.client_receive_service.receive(sock, data_length)
                        else:
                            # No data received, close the connection
                            print('Server closed the connection')
                            self.inputs.remove(sock)
                            sock.close()
                    except ServerError as e:
                        print(f'Server error: {e}')
                    except socket.error as e:
                        print(f'Socket error: {e}')
                        self.inputs.remove(sock)
                        sock.close()
                    except pickle.PickleError as e:
                        print(f'Error deserializing data: {e}')

    def send(self, data):
        try:
            data_bytes = pickle.dumps(data)
            data_length = len(data_bytes)
            header = f'{data_length:<{self.HEADER_LENGTH}}'.encode('utf-8')
            self.client_socket.sendall(header + data_bytes)
        except pickle.PickleError as e:
            print(f'Error serializing data: {e}')
        except socket.error as e:
            print(f'Socket error: {e}')

    def close(self):
        self.client_socket.close()


class ClientCLI:
    def __init__(self, client_instance):
        self.client_instance = client_instance

    def run(self):
        print("Client CLI running")
        print("COMMANDS:")
        print("1. Create session")
        print("2. Join session")
        print("3. Leave session")
        print("4. Roll dice")
        print("5. Make move")
        print("6. Exit")
        print("clear: Clear the screen")
        while True:
            command = input("")
            match command:
                case "1":
                    self.client_instance.client_request_service.create_session_request()
                case "2":
                    session_code = input("Enter session code: ")
                    self.client_instance.client_request_service.join_session_request(session_code)
                case "3":
                    self.client_instance.client_request_service.leave_session_request()
                case "4":
                    self.client_instance.client_request_service.roll_dice_request()
                case "5":
                    try:
                        number_1 = int(input("Enter move one: "))
                        number_2 = int(input("Enter move two (type 0 if you want just one number): "))
                        move = [number_1]
                        if number_2:
                            move.append(number_2)
                    except ValueError:
                        print("Invalid value, please enter a number")
                        continue
                    self.client_instance.client_request_service.make_move_request(move)
                case "6":
                    self.client_instance.close()
                    break
                case "7":
                    os.system('cls')
                    print("Client CLI running")
                    print("COMMANDS:")
                    print("1. Create session")
                    print("2. Join session")
                    print("3. Leave session")
                    print("4. Roll dice")
                    print("5. Make move")
                    print("6. Exit")
                    print("clear: Clear the screen")
                case _:
                    print("Invalid command")


client = Client()
client_thread = threading.Thread(target=client.receive)
client_thread.start()

client_cli = ClientCLI(client)
client_cli_thread = threading.Thread(target=client_cli.run)
client_cli_thread.start()

