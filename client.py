import asyncio
import getpass
import json
import os

import websockets

# Next 4 lines are not needed for AI agents, please remove them from your code!
import pygame

pygame.init()
program_icon = pygame.image.load("data/icon2.png")
pygame.display.set_icon(program_icon)


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

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )

                for item in state["game"]:
                    if item[1] == 29 and item[0] in array_of_taken:
                        array_of_taken.remove(item[0])
                # print(array_of_taken)

                minu_y = 0
                minu_x = 0
                len_counter = 1
                # dlugosc podstawy
                if state["piece"] is not None:
                    for item in state["piece"]:
                        if item[1] > minu_y:
                            minu_y = item[1]
                            minu_x = item[0]
                            len_counter = 1
                        elif item[1] == minu_y:
                            len_counter += 1
                    print("najnizszy pk: ", minu_y, "jego dlugosc: ", len_counter)

                dziura_len = 1
                start_x = array_of_taken[0]
                # nowa_dziura = True
                # sprawdzanie długości dziury
                print("array przed dodaniem:", array_of_taken)
                for i in range(len(array_of_taken)-1):
                    if array_of_taken[i+1] - array_of_taken[i] == 1:
                        dziura_len += 1
                    else:
                        print("nowa dziura")
                        dziura_len = 1
                        start_x = array_of_taken[i+1]
                print("dlugosc dziury: ", dziura_len, 'początek: ', start_x)

                if len_counter < dziura_len:
                    minu_x = start_x
                times = minu_x -1
                print(minu_x, "min x")
                print("time: ", times)

                # poruszanie sie
                if 4 - start_x > 0:
                    key = "a"

                elif 4 - start_x < 0:
                    key = "d"

                # if times > 0:
                #     key = "a"
                # elif times < 0:
                #     key = "d"
                times = abs(4 - start_x)
                print("times ", times)
                # + times - go left
                # - times - go right

                for i in range(1):
                    print("DUPAAA", i)
                    await websocket.send(
                        json.dumps({"cmd": "key", "key": key})
                    )
                key = ""

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
