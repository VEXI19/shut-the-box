import os
import threading

# run this to start the server and two clients

client_thread_1 = threading.Thread(target=os.system, args=('start /wait cmd /k "python ./client/client.py"',))
client_thread_2 = threading.Thread(target=os.system, args=('start /wait cmd /k "python ./client/client.py"',))
server_thread = threading.Thread(target=os.system, args=('start /wait cmd /k "python ./server/server.py"',))

client_thread_1.start()
client_thread_2.start()
server_thread.start()
