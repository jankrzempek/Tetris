import asyncio
from asyncio.locks import Event
from asyncio.tasks import sleep
import getpass
import json
import os
from pygame import event
from shape import Shape
import math
import websockets

# Next 4 lines are not needed for AI agents, please remove them from your code!
import pygame

pygame.init()
program_icon = pygame.image.load("data/icon2.png")
pygame.display.set_icon(program_icon)


def rotate(origin, point, angle):

    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    print("zmienione koordynaty: ", qx, qy)
    return qx, qy


def najdluzsza_dziura(array):
    najdluzszy_ciag = 0
    pierwsza_wartosc = 1
    wartosc = 1
    element = 1

    for i in range(len(array)-1):
        if array[i+1] - array[i] == 1:
            wartosc +=1
            if wartosc > najdluzszy_ciag:
                najdluzszy_ciag = wartosc
        else:
            element = i + 1
            wartosc = 1


    pierwsza_wartosc = element

    return najdluzszy_ciag, pierwsza_wartosc



async def agent_loop(server_address="localhost:8001", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        # Next 3 lines are not needed for AI agent
        SCREEN = pygame.display.set_mode((299, 123))
        SPRITES = pygame.image.load("data/pad.png").convert_alpha()
        SCREEN.blit(SPRITES, (0, 0))
        array_of_taken = [1, 2, 3, 4, 5, 6, 7, 8]
        key = ""
        piece_current = 0
        score = 0
        # Outside loop
        pressed = False

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )
                key = ""
                for item in state["game"]:
                    if item[1] == 29 and item[0] in array_of_taken:
                        array_of_taken.remove(item[0])
                # print(array_of_taken)
                if len(array_of_taken) == 0:
                    array_of_taken = [1, 2, 3, 4, 5, 6, 7, 8]

                minu_y = 0
                minu_x = 0
                len_counter = 1
                if score != state['score']:
                    array_of_taken = [1, 2, 3, 4, 5, 6, 7, 8]
                    score = state['score']
                # dlugosc podstawy
                if state["piece"] is not None:
                    for item in state["piece"]:
                        # print("nie zmienione: ", item)
                        # zmienione = rotate(item, (0, 0), 90)
                        # print(zmienione)
                        if item[1] > minu_y:
                            minu_y = item[1]
                            minu_x = item[0]
                            len_counter = 1
                        elif item[1] == minu_y:
                            len_counter += 1
                print("najnizszy pkt: ", minu_x, minu_y)
                print("array: ", array_of_taken)

                dziura_len = 1
                najdluzsza_dziura = [-1, 0]
                start_x = array_of_taken[0]
                # sprawdzanie długości dziury
                for i in range(len(array_of_taken)-1):
                    if array_of_taken[i+1] - array_of_taken[i] == 1:
                        dziura_len += 1
                    else:
                        print("nowa dziura")
                        dziura_len = 1
                        start_x = array_of_taken[i+1]
                print("dlugosc dziury: ", dziura_len, 'początek: ', start_x)

                if piece_current != len(state["game"]):
                    tablica = state["game"]
                    ostatnie = tablica[-4:]
                    minu_y = 0
                    minu_x = 0
                    print("ostatnie: ", ostatnie)
                    for item in ostatnie:
                        if item[1] > minu_y:
                            minu_y = item[1]
                            minu_x = item[0]
                    print(minu_x, minu_y)
                    for y in range(0, minu_y):
                        if (minu_x-1, y) in tablica:
                            print("ten po lewej")
                            if (minu_x-1) in array_of_taken:
                                array_of_taken.remove(minu_x-1)
                        print(minu_x+1)
                        print(minu_y-1)
                        if (minu_x+1, y) in tablica:
                            print("ten po prawej")
                            if (minu_x+1) in array_of_taken:
                                array_of_taken.remove(minu_x+1)
                    piece_current += 4

                print("dziura: ", najdluzsza_dziura, "klocek: ", len_counter)
                print("start dziury: ", start_x)
                print("min x: ", minu_x)
                times = abs(4 - start_x)

                # poruszanie sie
                if 4 - start_x > 0 and start_x-minu_x < 0:
                    key = "a"

                elif 4-start_x > 0 and start_x-minu_x > 0:
                    key = "d"

                elif 4 - start_x < 0 and start_x-minu_x != 0:
                    key = "d"

                else:
                    pass

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

            pygame.display.flip()







# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8001")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
