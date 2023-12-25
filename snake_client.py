import socket
import pygame
import sys
import threading

# function to parse game state received from server into x and y variables to use for drawing the interface.
def parse_tuple(t):
    x, y = map(int, t.strip('()').split(','))
    return x, y

# function to draw each cube on the game interface.
def draw(x, y, w, rows, colour, surface, eyes=False):
    # find the dis from width and rows to calculate where each cube's position should be.
    dis = w // rows
    pygame.draw.rect(surface, colour, (x*dis+1, y*dis+1, dis-2, dis-2))

    # if this cube has eyes, draw its eyes.
    if eyes:
        centre = dis // 2
        radius = 3
        circleMiddle = (x * dis + centre - radius, y * dis + 8)
        circleMiddle2 = (x * dis + dis - radius * 2, y * dis + 8)
        pygame.draw.circle(surface, (0, 0, 0), circleMiddle, radius)
        pygame.draw.circle(surface, (0, 0, 0), circleMiddle2, radius)

# function to draw grid lines on the game interface.
def drawGrid(w, rows, surface):
    sizeBtwn = w // rows
    x = 0
    y = 0

    for l in range(rows):
        x = x + sizeBtwn
        y = y + sizeBtwn

        pygame.draw.line(surface, (255, 255, 255), (x, 0), (x, w))
        pygame.draw.line(surface, (255, 255, 255), (0, y), (w, y))

# function that will draw the entire display of game interface.
def redrawWindow(surface, gameState):
    global width, rows, snakeColour, snackColour
    surface.fill((0, 0, 0))
    # draw the grids.
    drawGrid(width, rows, surface)

    # parse gameState into a list of snake cube position and snack cube positions.
    snake_str, snack_str = gameState.split("|", 1)

    # split snake_str by '**' to get a list of strings each representing a snake.
    snakes_data = snake_str.split('**')

    # iterate each snake's data to get its cube positions.
    for snake_data in snakes_data:
        snake_positions = [parse_tuple(pos) for pos in snake_data.split('*')]

        for i, (x, y) in enumerate(snake_positions, start=0):
            # if head of snake, draw eyes.
            if i == 0:
                draw(x, y, width, rows, snakeColour, surface, True)
            else:
                draw(x, y, width, rows, snakeColour, surface)

    # draw snack cubes.
    snackList = [parse_tuple(snack) for snack in snack_str.split('**')]

    for i, (x, y) in enumerate(snackList, start=0):
        draw(x, y, width, rows, snackColour, surface)

    # update the display.
    pygame.display.update()

# function to handle client inputs for movement and communication.
def move(client):
    # constantly accept user keyboard inputs and send respective inputs to server.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            pygame.display.quit()
            sys.exit()

        # if a key is pressed by user, send respective input commands to server.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                client.send("up".encode('ascii'))
                return

            elif event.key == pygame.K_DOWN:
                client.send("down".encode('ascii'))
                return

            elif event.key == pygame.K_RIGHT:
                client.send("right".encode('ascii'))
                return

            elif event.key == pygame.K_LEFT:
                client.send("left".encode('ascii'))
                return

            elif event.key == pygame.K_q:
                client.send("quit".encode('ascii'))
                return

            elif event.key == pygame.K_r:
                client.send("reset".encode('ascii'))
                return

            elif event.key == pygame.K_z:
                client.send("Congratulations!".encode('ascii'))
                return

            elif event.key == pygame.K_x:
                client.send("It works!".encode('ascii'))
                return

            elif event.key == pygame.K_c:
                client.send("Ready?".encode('ascii'))
                return

    # if no key is pressed by user, send default command "get" to server.
    client.send("get".encode('ascii'))

def main():
    # connect client to server.
    server = "localhost"
    port = 5555

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server, port))

    # variables needed to display game.
    global width, rows, snakeColour, snackColour, clock, win
    width = 500
    rows = 20
    snakeColour = (255, 0, 0)
    snackColour = (0, 255, 0)
    win = pygame.display.set_mode((width, width))
    clock = pygame.time.Clock()

    while True:
        # add delays to game display
        clock.tick(9)

        data = client.recv(1024).decode()

        # if received data from server contains "message=", consider it a public message to print.
        if data.startswith("message="):
            messages = data.split("=", 1)[1].split("\nmessage=")
            for message in messages:
                if message:
                    print(message)

        # if public message and game state were sent at the same time, parse to update game and display message.
        elif "message=" in data:
            parts = data.split("message=")
            game_state = parts[0].strip()
            message = "message=" + parts[1].strip()

            redrawWindow(win, game_state)

            messages = message.split("=", 1)[1].split("\nmessage=")
            for message in messages:
                if message:
                    print(message)

        # if no public message was sent, just update game.
        else:
            # draw game interface
            redrawWindow(win, data)

        move(client)

main()
