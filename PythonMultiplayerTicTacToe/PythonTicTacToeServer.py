import socket
import threading

# Game board
board = [" " for _ in range(9)]
players = {}
current_turn = None

# Function to check win condition
def check_winner():
    win_patterns = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for (a, b, c) in win_patterns:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return None

def print_board(p_conn):
    board_string = ""
    board_space = 0
    for _ in board:
        if board_space == 0:
            board_string += "["
        board_string += "'"+_+"'"
        board_space += 1
        if board_space == 3:
            board_string += "]\n"
            board_space = 0
    p_conn.sendall(board_string.encode())

# Function to handle player moves
def handle_client(conn, addr, player_symbol):
    global current_turn
    awaiting_turn = False

    conn.sendall(f"Welcome! You are Player {player_symbol}. Waiting for the other player...\n".encode())

    while len(players) < 2:
        pass  # Wait for second player

    conn.sendall("Game has started! Here's the board:\n".encode())
    
    for p_conn in players.values():
        print_board(p_conn)

    while True:
        if current_turn == player_symbol:
            conn.sendall("Your turn! Enter a position (0-8): \n".encode())
            try:
                move = int(conn.recv(1024).decode().strip())
                if 0 <= move < 9 and board[move] == " ":
                    board[move] = player_symbol
                    current_turn = "O" if player_symbol == "X" else "X"
                else:
                    conn.sendall("Invalid move! Try again.\n".encode())
                    continue
            except ValueError:
                conn.sendall("Invalid input! Enter a number (0-8).\n".encode())
                continue

            # Broadcast updated board to both players
            for p_conn in players.values():
                print_board(p_conn)

            winner = check_winner()
            if winner:
                for p_conn in players.values():
                    p_conn.sendall(f"Player {winner} wins!\n".encode())
                break
        else:
            conn.sendall("Waiting for opponent's move...\n".encode())

    conn.close()

# Start server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5555))
server.listen(2)
print("Server started, waiting for players...")

while len(players) < 2:
    conn, addr = server.accept()
    player_symbol = "X" if len(players) == 0 else "O"
    players[player_symbol] = conn
    if len(players) == 1:
        current_turn = "X"
    
    threading.Thread(target=handle_client, args=(conn, addr, player_symbol)).start()