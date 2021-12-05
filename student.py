from shape import SHAPES
import copy
import asyncio
import getpass
import json
import os
from asyncio.locks import Event
from asyncio.tasks import sleep
import getpass
import json
import os
from pygame import event
from shape import Shape
import websockets

# Next 4 lines are not needed for AI agents, please remove them from your code!
import pygame
pygame.init()
program_icon = pygame.image.load("data/icon2.png")
pygame.display.set_icon(program_icon)

# ---------- NOT ASYNC ----------

def indicate_black_line(state):
    floor = [[1, 30], [2, 30], [3, 30], [4, 30], [5, 30], [6, 30], [7, 30], [8, 30]]
    black_line = []
    if state["game"]:
        y_threshold = min(state["game"], key=lambda item: item[1])[1]
        array_of_game_and_floor = state["game"] + floor
        black_line.append([0, y_threshold])
        # Collecting spiky point for every line
        for line in range(1, 9):
            local_min = 100
            for item in array_of_game_and_floor:
                if item[0] == line:
                    if item[1] < local_min:
                        local_min = item[1]
            black_line.append([line, local_min])
        black_line.append([9, y_threshold])
        # Making full line using them
        ## current y value - next y value = ?? sum
        ## sum < 0: Go down
        ## sum == 0: nothing, just next piece
        ## sum > 0: Go up
        ## [1] -> Y Value ; [0] -> X Value
        fullfill_black_line = []
        for spike in range(len(black_line) - 1):
            equal = black_line[spike][1] - black_line[spike + 1][1]
            if equal < 0: # Go DOWN
                for nn_y in range(abs(equal)):
                    fullfill_black_line.append([black_line[spike][0],
                                                black_line[spike][1] +  nn_y])
            if equal > 0: # Go UP
                for nn_y in (range(abs(equal))):
                    fullfill_black_line.append([black_line[spike + 1][0],
                                                black_line[spike][1]- nn_y])

        for item in fullfill_black_line: black_line.append(item)
        # Making into set not to have duplicates
        # black_line_completed = sorted(set(black_line))
        # for item in black_line: black_line_completed.add(item)
    else:
        # Black line when nothing is in the board yet is equal to blue line
        black_line = indicate_blue_line(state)
    return black_line

def indicate_blue_line(state):
    # Blue line is just the frame of the board
    floor = [[1, 30], [2, 30], [3, 30], [4, 30], [5, 30], [6, 30], [7, 30], [8, 30]]
    blue_line = []
    for i in range(31):
        blue_line.append([0, i])
    for f in floor:
        blue_line.append(floor)
    for i in reversed(range(31)):
        blue_line.append([9, i])
    return blue_line

def is_empty_line(game, x, y):
    for coordinate in game:
        if coordinate[0] == x and coordinate[1] < y:
            print("jest cos wyzej", x, y)
            return False
    return True

def coordinates(piece):
    x_min = 100
    y_min = 100
    x = 0
    y = 0
    new_piece = []
    x_min = min(piece, key=lambda item: item[0])[0]
    y_min = min(piece, key=lambda item: item[1])[1]
    for coordinate in piece:
        x = coordinate[0] - x_min
        y = coordinate[1] - y_min
        new_piece.append([x, y])
    return new_piece


def new_coordinates(piece, game, x, tablica, new_piece, y_min):
    if game:
        new_x, new_y = 0, 0
        tablica_x = [x[0] for x in piece]
        set_x = set(tablica_x)
        czy_tu_bylo = False
        y_max_piece = max(piece, key=lambda cos: cos[1])[1]
        czy_pod_nami_pusto = True
        # 0+x, y ; 1+x, y
        # znalesc najmniejszy z tych y
        tablica_x_z_game = []
        for item in set_x:
            tablica_danej_linii = []
            for element in game:
                if element[0] == item+x:
                    tablica_danej_linii.append(element)
            if tablica_danej_linii:
                y_thre = min(tablica_danej_linii, key=lambda cos: cos[1])
            if not tablica_danej_linii:
                y_thre = [item+x, 30]
            tablica_x_z_game.append(y_thre)
        y_minimalne = min(tablica_x_z_game, key=lambda cos: cos[1])[1]
        # y_minimalne -= 1
        print("najnizszy pkt: ", y_minimalne)
        print("sprawdzamy klocka czy ma 4: ", piece)
        for coordinate in piece:
            # tu musimy sprawdzic wysokosci y

            new_x = coordinate[0] + x
            new_y = coordinate[1] + (y_minimalne - y_max_piece)
            print("nowe koordynaty które chcemy dodac: ", new_x, new_y)
            if is_empty_line(game, new_x, new_y):
                print("STATED EMPTY LINE")
                if new_y < y_min:
                    y_min = new_y
                if new_x > 8 or new_x < 1:
                    tablica.append([0, ['']])
                    break  # przerywamy wyznaczanie dla tego x
                if [new_x, new_y] in game:
                # to znaczy ze na któryms z miejsc jest juz inny klocek wiec 0 pkt i 0 przesuniec
                    ("przesuwamy sie o jeden wyzej bo tu jest zajęte", new_x, new_y)
                    # break  # przerywamy wyznaczanie dla tego x
                    czy_tu_bylo = True
                    print("TUUUUUUU BYŁOOOOOOOO")
                print("dodajemy wspolrzedne: ", new_x, new_y)
                # if [new_x, new_y-1] in game:
                #     czy_pod_nami_pusto = False
                new_piece.append([new_x, new_y])
            else:
                tablica.append([0, ['']])
                break  # przerywamy wyznaczanie dla tego x
        if czy_tu_bylo:
            for c in new_piece:
                c[1] -= 1
                print("ZOBACZ CZY ODJALEM Z TABLICY Y -1")
                print(new_piece)
                print(new_y)
        # if czy_pod_nami_pusto:
        #     for c in new_piece:
        #         c[1] += 1
        #         print("ZOBACZ CZY ODJALEM Z TABLICY Y -1")
        #         print(new_piece)
        #         print(new_y)
    return tablica, new_piece, y_min


def decision_function(piece, game, black_line, blue_line):
    '''
    piece - wspolrzedne klocka
    game - zamalowane klocki
    black line - współzedne graniczne klocków
    typy ruchów: obrót, ruch w bok

    jak przesuwamy klocka
    od lewej do prawej
    punkty do tablicy i liczba przesunięc (kluczy)
    znajdujemy najwyzej polozony y o danym x
    sprawdzamy czy pozostałe wspołzedne klocka po przesunięciu mozna tam wpasowac
    jak tak sprawdzamy jakie wspolzedne dotykają black line i liczymy pkt
    kazdy polozony klocek to 1 * dlugosc / wysokosc

    dodajemy do tablicy punkty i liste kluczy: jezelu 4-x > 0 to tyle razy w prawo jezeli < 0 to tyle razy w lewo jezeli nic to w dół
    '''
    tablica = []
    if piece is not None:
        # lecimy po kolei wspolrzedne x
        for x in range(1, 8):
            print("-------------------> ## DECISION: ", x, "\n")
            y_min = 100
            y_max = 30
            points = 0
            new_piece = []
            x_min = min(piece, key=lambda item: item[0])[0]
            print("min : ", x_min)
            # tu mamy najlizszy pkt y dla wybranego x
            # jak przesunac - znalesc najdalej wysuniety x jezeli x > 4 to przesuwamy w prawo x <
            y_thre = max(piece, key=lambda item: item[1])[1]
            basic_piece = coordinates(piece)
            print("KLOCEK w 0;0 :", basic_piece, "\n")


            tablica, new_piece, y_min = new_coordinates(basic_piece, game, x, tablica, new_piece, y_min)
            print("NEW_PIECE : ", new_piece, "\n")
            if len(tablica) != x:
                # wyznaczamy punkty
                for coordinate in new_piece:
                    sasiady = [[coordinate[0]+1, coordinate[1]],
                                [coordinate[0]-1, coordinate[1]],
                                [coordinate[0], coordinate[1]+1]]
                    print("sasiedzi: ", sasiady, "===============================")
                    print("# Punktacja za koordynaty:", coordinate)
                    for s in sasiady:
                        if s in blue_line and s in black_line:
                            points += 6
                            print("5 pkt za blue i black line")
                        else:
                            if s in black_line:
                                points += 6
                                print("6 pkt za black line")
                            elif s in blue_line:
                                points += 3
                                print("2 pkt za blue line")
                            else:
                                points += 1
                                print("1 pkt pozostałe")

                print("Podsumowanie punktacji: ", points, "\n")

                keys = []
                ile = abs(x - x_min)
                print("?? ile roznicy - przesuniecia: ", ile, "??\n")
                if x < x_min:
                    for i in range(ile):
                        keys.append("a")
                    print(keys)
                elif x > x_min:
                    for i in range(abs(ile)):
                        keys.append("d")
                    print(keys)

                # dodawanie do tablicy
                tablica.append([points, keys, y_min])

        sorted_table = sorted(tablica, reverse=True)
        powtorzenia = sorted_table.count(sorted_table[0][0])
        for i in range(powtorzenia):
            if sorted_table[0][2] > sorted_table[i][2]:
                sorted_table.pop(0)
        print("RUCHY KLOCKA :", sorted_table, "\n")
        return sorted_table[0][1]
    return []

def identify_block(state):
    # The aim of this function is to identify name of the falling block
    # We iterate over SHAPES to find out which one is falling
    # The key here -> is the difference between first |x|y| of falling piece and |x|y| of shape
    # If the taken difference satisfy all the other 3 coordinates points -> WE'VE GOT A BLOCK!
    # Deep copy is needed not to meesed up something in SHAPES
    current_block_coordinates = state["piece"]
    identity_val = current_block_coordinates[0]
    result = True
    for shape in SHAPES:
        owning_shape = copy.deepcopy(shape)
        result = True
        shape_identity = owning_shape.positions[0]
        leading_coordinates = (identity_val[0]-shape_identity[0], identity_val[1]-shape_identity[1])
        for s in range(4):
            if (current_block_coordinates[s][0] - owning_shape.positions[s][0] != leading_coordinates[0] or
                current_block_coordinates[s][1] - owning_shape.positions[s][1] != leading_coordinates[1]):
                result = False
                break
            else:
                result = True
        if result:
            # We are assigning a current piece position to shape so that we can
            # then easly operate on it (rotate, get name...)
            owning_shape.set_pos(leading_coordinates[0], leading_coordinates[1])
            print(owning_shape)
            print("[---BLOCK IDENTIFIED---]")
            return owning_shape

def initiate_block_rotation(pass_shape, times):
    # Having shave in Shape class we are able to rotate it
    # Based on user passed 'times' parameter we decide how many times we will rotate
    pass_shape.rotate(times)
    print("ROTATED |x|y|", pass_shape)
    return pass_shape.positions

def play(state, keys, is_new_piece):
    key = ""
    current_black_line = indicate_black_line(state)
    current_blue_line = indicate_blue_line(state)
    if state["piece"] is None:
        is_new_piece = True
    if state["piece"] is not None and is_new_piece == True:
        print("## IDENTIFYING BLOCK & ROTATION...")
        block = identify_block(state)
        initiate_block_rotation(block, times=1)
        print("## FINISH IDENTIFYING!\n\n")
        print("## BLACK LINE")
        print(current_black_line)
        print("## END OF BLACK LINE\n\n")
        keys = decision_function(state["piece"], state["game"], current_black_line, current_blue_line)
        print("KEYS", keys)
        is_new_piece = False

    if len(keys) != 0:
        key = keys[0]
        print(key)
        keys.remove(key)
        print(keys)
    return key, keys, is_new_piece


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        # Next 3 lines are not needed for AI agent
        SCREEN = pygame.display.set_mode((299, 123))
        SPRITES = pygame.image.load("data/pad.png").convert_alpha()
        SCREEN.blit(SPRITES, (0, 0))

        key = ""
        keys = []
        is_new_piece = True

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )

                if "game" in state.keys():
                    key, keys, is_new_piece = play(state, keys, is_new_piece)
                    await websocket.send(
                        json.dumps({"cmd": "key", "key": key})
                    )

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

            pygame.display.flip()

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))