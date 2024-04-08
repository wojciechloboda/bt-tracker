
import socket
import threading
import time

SERVER_PORT = 9000
HOST = ''

def receive_from_client(client_socket):
    while True:
        chunk = client_socket.recv(1024)
        print("GOT: ", chunk)
        time.sleep(0.5)


def accept_connections():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, SERVER_PORT))
    server_socket.listen(3)

    while True:
        client_socket, _ = server_socket.accept()
        print("GOT CONNECTION FROM CLIENT")
        client_thread = threading.Thread(target=receive_from_client, args=(client_socket,))
        client_thread.start()

if __name__ == '__main__':
    accept_connections()



