'''
    Project developed by:
    Maja Szymajda - 806800
    Jan Krzempek - 806835
'''
from shape import SHAPES
import copy
import asyncio
import getpass
import json
import os
import getpass
import json
import os
import websockets
import pygame

pygame.init()
program_icon = pygame.image.load("data/icon2.png")
pygame.display.set_icon(program_icon)

# ---------- FUNCTIONS ----------
floor = [[1, 30], [2, 30], [3, 30], [4, 30], [5, 30], [6, 30], [7, 30], [8, 30]]

def indicate_black_line(state):
    ''' 
        Making full line using blocks
        current y value - next y value = ?? sum
        sum < 0: Go down
        sum == 0: nothing, just next piece
        sum > 0: Go up
        [1] -> Y Value ; [0] -> X Value
    '''
    black_line = []
    if state["game"]:
        array_of_game_and_floor = state["game"] + floor
        # Collecting spiky point for every line
        for line in range(1, 9):
            local_min = 100
            for item in array_of_game_and_floor:
                if item[0] == line and item[1] < local_min:
                    local_min = item[1]
            black_line.append([line, local_min])
        fullfill_black_line = []
        for spike in range(len(black_line) - 1):
            equal = black_line[spike][1] - black_line[spike + 1][1]
            # Go DOWN
            [ fullfill_black_line.append([black_line[spike][0], black_line[spike][1] + nn_y]) for nn_y in range(abs(equal)) if equal < 0 ]
            # Go UP
            [ fullfill_black_line.append([black_line[spike + 1][0], black_line[spike][1] - nn_y]) for nn_y in range(abs(equal)) if equal > 0 ]

        [ black_line.append(item) for item in fullfill_black_line ]
    else:
        # Black line when nothing is in the board yet is equal to blue line
        black_line = indicate_blue_line()
    return black_line


def indicate_blue_line():
    # Blue line is just the frame of the board
    blue_line = []
    [ blue_line.append([0, i]) for i in range(31) ]
    [ blue_line.append(f) for f in floor ]
    [ blue_line.append([9, i]) for i in reversed(range(31)) ]
    return blue_line


def is_empty_line(game, x, y):
    return [False if coordinate[0] == x and coordinate[1] < y else True for coordinate in game]


def coordinates(piece):
    new_piece = []
    x_min = min(piece, key=lambda item: item[0])[0]
    y_min = min(piece, key=lambda item: item[1])[1]
    for coordinate in piece:
        x = coordinate[0] - x_min
        y = coordinate[1] - y_min
        new_piece.append([x, y])
    return new_piece


def new_coordinates(piece, game, x, y_min, black_line, mała_tablica):
    if game:
        new_x, new_y = 0, 0
        tablica_x = [x[0] for x in piece]  # sprawdzamy szerokosc klocka
        set_x = set(tablica_x)
        czy_tu_bylo = False  # jezeli znajdziemy chociaz jedno pole zajete bedzie true i dodamy pole nad nim
        czy_pod_nami_pusto = True # sprawdzamy czy przypadkiem pozycja pod nami nie jest pusta
        y_max_piece = max(piece, key=lambda cos: cos[1])[1]  # najnizszy y z naszego klocka sluzy do wyznaczenia koordynatow
        tablica_x_z_game = []
        # 0+x, y ; 1+x, y
        # znalesc najmniejszy z tych y

        for item in set_x:  # dla kazdego x z naszego klocka
            tablica_danej_linii = []  # wszystkie miejsca zajete pod nami w danej lini dla kazdego x z szerokosci klocka
            [ tablica_danej_linii.append(element) for element in game if element[0] == item+x ]
            y_thre = min(tablica_danej_linii, key=lambda cos: cos[1])  if tablica_danej_linii else [item+x, 30] 
            # jezeli go nie ma to pole jest puste i jedziemy na sam dół 30 bo ustawiamy sie jeden wyzej niz zajety klocek
            tablica_x_z_game.append(y_thre) # zajmuje ją lista najwyzej polozonych pkt dla danej pozycji klocka, jego szerokosci
        y_minimalne = min(tablica_x_z_game, key=lambda cos: cos[1])[1] # znajduje najwyzej polozony pkt - tzw pkt oparcia dla klocka
        new_piece = []

        for coordinate in piece:
            # tu musimy sprawdzic wysokosci
            new_x = coordinate[0] + x
            new_y = coordinate[1] + (y_minimalne - y_max_piece)
            if is_empty_line(game, new_x, new_y):
                if new_y < y_min:   # to jest tylko do zwrotki koncowej odpowiada za najnizszy y dodawany do tablicy
                    y_min = new_y
                if new_x > 8 or new_x < 1:
                    mała_tablica.append([0, ['']])
                    new_piece = []
                    y_min = 100
                    return mała_tablica, new_piece, y_min   # przerywamy wyznaczanie dla tej pozycji dla danego x wracamy do f głownej
                if [new_x, new_y] in game or new_y == 30:   # to znaczy ze na któryms z miejsc jest juz inny klocek wiec 0 pkt i 0 przesuniec
                    czy_tu_bylo = True
                new_piece.append([new_x, new_y])
            else:
                mała_tablica.append([0, ['']])
                new_piece = []
                y_min = 100
                return mała_tablica, new_piece, y_min   # przerywamy wyznaczanie dla tej pozycj
                                                        # jakikolwiek klocek nad nami
                                                        # przesuwamy sie o jedno w gore bo cos było na naszym poziomie
        if czy_tu_bylo:
            for c in new_piece:
                c[1] -= 1
            y_min -= 1

        # pusta przestrzen pod klockiem
        for cy in new_piece:
            if [cy[0], cy[1]+1] in game or [cy[0], cy[1]+1] in black_line:
                czy_pod_nami_pusto = False

        # pod nami wolne mozna isc nizej
        if czy_pod_nami_pusto:
            for c in new_piece:
                c[1] += 1
            y_min += 1
    else:
        # pierwszy klocek, game jest puste
        new_piece = []
        y_max_piece = max(piece, key=lambda cos: cos[1])[1]
        for coordinate in piece:    # tu musimy sprawdzic wysokosci y
            new_x = coordinate[0] + 1
            new_y = coordinate[1] + 29 - y_max_piece
            new_piece.append([new_x, new_y])
    return mała_tablica, new_piece, y_min


def count_points(new_piece, blue_line, black_line, points, game):
    for coordinate in new_piece:
        sasiady = [[coordinate[0] + 1, coordinate[1]],
                    [coordinate[0] - 1, coordinate[1]],
                    [coordinate[0], coordinate[1] + 1]]
        for s in sasiady:
            if s in black_line:
                points += 6.0
            elif s in blue_line:
                points += 4.0
            else:
                points += 1.0

        y_table = [ y for y in game if y[1] == coordinate[1] ]
        [ y_table.append(c) for c in new_piece if c[1] == coordinate[1]]

        if len(y_table) == 8:
            points += 15

    return points


def identify_block(state):
    '''
        The aim of this function is to identify name of the falling block
        We iterate over SHAPES to find out which one is falling
        The key here -> is the difference between first |x|y| of falling piece and |x|y| of shape
        If the taken difference satisfy all the other 3 coordinates points -> WE'VE GOT A BLOCK!
        Deep copy is needed not to meesed up something in SHAPES
    '''
    current_block_coordinates = state["piece"]
    identity_val = current_block_coordinates[0]
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
            return owning_shape


def indentify_keys(x, x_min, rotate, y_min):
    keys = []
    ile = abs(x - x_min)
    [ keys.append("w") for _ in range(rotate) ]
    if x < x_min:
        [ keys.append("a") for _ in range(abs(ile)) ]
    elif x > x_min:
        [ keys.append("d") for _ in range(abs(ile)) ]
    # DEBUG - should be
    if y_min > 15:
        keys.append("s")

    return keys


def decision_function(piece, game, black_line, blue_line, block):
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
        for x in range(1, 9):
            # jak przesunac - znalesc najdalej wysuniety x jezeli x > 4 to przesuwamy w prawo x <
            # Rotating a piece ang getting all it's possible positions (clockwise)
            rotated_piece = copy.deepcopy(block)
            table_positions = [piece]

            if rotated_piece:
                for i in range(3):
                    rotated_piece.rotate(1)
                    table_positions.append(rotated_piece.positions)

            rotate = 0
            mała_tablica = []  # tutaj wpisujemy 4 pozycje jednego klocka dla danego x

            for rotated in table_positions:
                points = 0
                basic_piece = coordinates(rotated)
                y_min = 100
                x_min = min(rotated, key=lambda item: item[0])[0]
                # sprawdzenie najbardziej korzystnej pozycji
                mała_tablica, new_piece, y_min = new_coordinates(basic_piece, game, x, y_min, black_line, mała_tablica)

                if len(mała_tablica) != rotate + 1 and len(new_piece) == 4:
                    points = count_points(new_piece, blue_line, black_line, points, game)
                    keys = indentify_keys(x, x_min, rotate, y_min)
                    mała_tablica.append([points, keys, y_min]) # dla kazdego z 4 rotacji klocka dodajemy do tablicy inf
                rotate += 1

            sorted_small_table = sorted(mała_tablica, reverse=True)
            best_option = sorted_small_table[0]
            tablica.append(best_option)

        sorted_table = sorted(tablica, reverse=True)
        powtorzenia = sorted_table.count(sorted_table[0][0])
        [ sorted_table.pop(0) for i in range(powtorzenia) if sorted_table[0][2] > sorted_table[i][2] ]
        return sorted_table[0][1]
    return []


def play(state, keys, is_new_piece):
    key = ""
    if state["piece"] is None:
        is_new_piece = True
    if state["piece"] is not None and is_new_piece == True:
        current_black_line = indicate_black_line(state)
        current_blue_line = indicate_blue_line()
        block = identify_block(state)
        keys = decision_function(state["piece"], state["game"], current_black_line, current_blue_line, block)
        is_new_piece = False
    if len(keys) != 0:
        key = keys[0]
        keys.remove(key)

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