import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5555))

while True:
    message = client.recv(1024).decode()
    print(message)

    if "Enter a position" in message:
        move = input("> ")
        client.sendall(move.encode())