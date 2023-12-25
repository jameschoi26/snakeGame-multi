import numpy as np
import socket
from _thread import *
import pickle
from snake import SnakeGame
import uuid
import time
import threading

# server = "10.11.250.207"
server = "localhost"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

counter = 0 
rows = 20 

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(5)
# s.settimeout(0.5)
print("Waiting for a connection, Server Started")

clients = [] # list to add the connected clients.

game = SnakeGame(rows)
game_state = "" 
last_move_timestamp = time.time()
interval = 0.2
moves_queue = set()

def handle_game():
    global game, moves_queue, game_state 
    while True:
        last_move_timestamp = time.time()
        game.move(moves_queue)
        moves_queue = set()
        game_state = game.get_state()
        while time.time() - last_move_timestamp < interval:
            time.sleep(0.1) 



rgb_colors = {
    "red" : (255, 0, 0),
    "green" : (0, 255, 0),
    "blue" : (0, 0, 255),
    "yellow" : (255, 255, 0),
    "orange" : (255, 165, 0),
} 
rgb_colors_list = list(rgb_colors.values())

# function to send all clients public messages.
def broadcast(message):
    for client in clients:
        client.send(message)

# function to handle client functions
def handle_client(client, unique_id):
    while True:
        data = client.recv(1024).decode()

        move = None

        if not data:
            print("no data received from client")
            break

        # default get message to send game state to client.
        elif data == "get":
            print("received get")
            client.send(game_state.encode())

        # if client requests to quit, remove the client from the game and server and clients list.
        elif data == "quit":
            print("received quit")
            game.remove_player(unique_id)
            clients.remove(client)
            client.close()
            broadcast(f'message=User {unique_id} left the game!'.encode('ascii'))
            break

        # if client requests to reset, reset the game board and send game state to client.
        elif data == "reset":
            game.reset_player(unique_id)
            client.send(game_state.encode())

        # if client requests an input movement, change their position on the board and send game state to client.
        elif data in ["up", "down", "left", "right"]:
            move = data
            moves_queue.add((unique_id, move))
            client.send(game_state.encode())

        # if client requests public messages, broadcast the respective message.
        elif data == "Congratulations!":
            broadcast(f'message=User {unique_id} says: {data}'.encode('ascii'))

        elif data == "It works!":
            broadcast(f'message=User {unique_id} says: {data}'.encode('ascii'))

        elif data == "Ready?":
            broadcast(f'message=User {unique_id} says: {data}'.encode('ascii'))

        else:
            print("Invalid data received from client:", data)

    client.close()

def main():
    global counter, game

    # Accepting all connections at all times.
    while True:
        client, addr = s.accept()
        print("Connected with:", addr)

        unique_id = str(uuid.uuid4())
        color = rgb_colors_list[np.random.randint(0, len(rgb_colors_list))]
        game.add_player(unique_id, color=color)

        # add connected client to clients list and display opening messages.
        clients.append(client)
        broadcast(f'message=User {unique_id} joined the game.\n'.encode('ascii'))
        client.send('message=Connected to the server.\n'.encode('ascii'))
        client.send('message=To communicate to others press hit the respective button shown below:\n'.encode('ascii'))
        client.send('message=z : "Congratulations!"\n'.encode('ascii'))
        client.send('message=x : "It works!"\n'.encode('ascii'))
        client.send('message=c : "Ready?"\n'.encode('ascii'))
        client.send('message=To disconnect, please hit button: q\n'.encode('ascii'))

        # separate threads to handle the game component and client component.
        game_thread = threading.Thread(target=handle_game)
        game_thread.start()

        thread = threading.Thread(target=handle_client, args=(client, unique_id))
        thread.start()


if __name__ == "__main__":
    main()
