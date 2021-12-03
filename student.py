from shape import SHAPES
import copy

class Agent:
    key = ""
    keys = []
    is_new_piece = True

    async def play(self, state):
       # Parametry
        self.key = ""

        current_blackL = self.indicate_black_line(state)
        if state["piece"] is None:
            self.is_new_piece = True
        if state["piece"] is not None and self.is_new_piece == True:
            print("## IDENTIFYING BLOCK & ROTATION...")
            block = self.identify_block(state)
            self.initiate_block_rotation(block, times=1)
            print("## FINISH IDENTIFYING!")
            self.keys = self.decision_function(state["piece"], state["game"], current_blackL)
            print("KEYS", self.keys)
            self.is_new_piece = False

        if len(self.keys) != 0:
            self.key = self.keys[0]
            print(self.key)
            self.keys.remove(self.key)
            print(self.keys)
        return self.key
        
# ---------- NOT ASYNC ----------
    def coordinates(self, piece):
        print("uwaga: ", piece)
        x_min = 100
        y_min = 100
        x = 0
        y = 0
        new_piece = []
        x_min = min(piece, key=lambda item: item[1])[0]
        y_min = max(piece, key=lambda item: item[1])[1]
        for coordinate in piece:
            x = coordinate[0] - x_min
            y = coordinate[1] - y_min
            new_piece.append([x, y])
        return new_piece

    def indicate_black_line(self, state):
        floor = [[1, 30], [2, 30], [3, 30], [4, 30], [5, 30], [6, 30], [7, 30], [8, 30]]
        black_line = []
        if state["game"] != []:
            y_threshold = min(state["game"], key=lambda item:item[1])[1]
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
            # Black line when nothing is in the board yet
            for i in range(31):
                black_line.append([0, i])
            for f in floor:
                black_line.append(floor)
            for i in reversed(range(31)):
                black_line.append([9, i])
        return black_line


    def decision_function(self, piece, game, black_line):
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
                print(x)
                y_max= 30
                points = 0
                new_piece = []
                x_min = min(piece, key=lambda item: item[1])[0]
                for item in black_line:
                    if item[0] == x and y_max >= item[1]:
                        y_max = item[1]-2
                        print(x, y_max, "wlazlem")
                # tu mamy najlizszy pkt y dla wybranego x
                # jak przesunac - znalesc najdalej wysuniety x jezeli x > 4 to przesuwamy w prawo x <
                y_thre = max(piece, key=lambda item:item[1])[1]

                # for coordinate in piece:
                #     print(coordinate, " halkoooooooo")

                #     if [coordinate[0]+o_ile_przesuwamy, coordinate[1]+ o_ile_przes_y] in game:
                #         # to znaczy ze na któryms z miejsc jest juz inny klocek wiec 0 pkt i 0 przesuniec
                #         tablica.append([0,['']])
                #         break  # przerywamy wyznaczanie dla tego x

                #     new_piece.append([coordinate[0]+o_ile_przesuwamy, coordinate[1] + o_ile_przes_y])
                print(piece)
                basic_piece = self.coordinates(piece)
                new_x, new_y = 0, 0
                for coordinate in basic_piece:
                    new_x = coordinate[0] + x
                    new_y = coordinate[1] + y_max
                    if [new_x, new_y] in game:
                    # to znaczy ze na któryms z miejsc jest juz inny klocek wiec 0 pkt i 0 przesuniec
                        tablica.append([0, ['']])
                        break  # przerywamy wyznaczanie dla tego x
                    new_piece.append([new_x, new_y])

                # wyznaczamy punkty
                for coordinate in new_piece:
                    print(coordinate, "nowe koordynaty")
                    if ([coordinate[0]+1, coordinate[1]] not in black_line) and ([coordinate[0], coordinate[1]+1] not in black_line) and ([coordinate[0]-1, coordinate[1]] not in black_line):
                        points += 1
                    #     print("mam 3 pkt")
                    if ([coordinate[0]+1, coordinate[1]] in black_line):
                        points += 3
                        print("mam 3 pkt za: ", [coordinate[0]+1, coordinate[1]])
                    if ([coordinate[0], coordinate[1]+1] in black_line):
                        points += 3
                        print("mam 3 pkt za: ", [coordinate[0], coordinate[1]+1])
                    if ([coordinate[0]-1, coordinate[1]] in black_line):
                        points += 3
                        print("mam 3 pkt za: ", [coordinate[0]-1, coordinate[1]])
                    # else:
                    #     points += 1

                print("punkty: ", points)
                # wyznaczamy przeduniecie
                keys = []
                print()
                ile = abs(x - x_min)
                print("ile roznicy: ", ile)
                if x < x_min:
                    print("dodaje w lewo")
                    for i in range(ile):
                        keys.append("a")
                    print(keys)
                elif x > x_min:
                    print("dodaje")
                    for i in range(abs(ile)):
                        keys.append("d")
                    print(keys)

                # dodawanie do tablicy
                tablica.append([points, keys])
                print(tablica)
            sorted_table = sorted(tablica, reverse=True)
            print(sorted_table)
            return sorted_table[0][1]
        return []

    def identify_block(self, state):
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
    
    def initiate_block_rotation(self, pass_shape, times):
        # Having shave in Shape class we are able to rotate it
        # Based on user passed 'times' parameter we decide how many times we will rotate
        pass_shape.rotate(times)
        print("ROTATED |x|y|", pass_shape)
        return pass_shape.positions





