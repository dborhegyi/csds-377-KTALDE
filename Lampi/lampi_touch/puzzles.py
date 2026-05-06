import random

class Puzzle_Handler:
    puzzle_codes = []
    puzzle_algorithms = {}
    puzzle_layouts = []


    def solve_puzzle(self, puzzle_code: str) -> str:
        if puzzle_code not in self.puzzle_codes:
            print("Error: puzzle code does not exist!")
            return

    def led_puzzle_config(self):
        #KEY:
        #Colors: red(0.0-0.1), yellow(0.2-0.3), blue(0.5-0.6), purple(0.7-0.8)
        #Saturation: Light(0.0-0.3), Muted(0.4-0.6), Saturated(0.7-1.0)
        #Brightness: Dim(0.0-0.3), Moderate(0.4-0.6), Bright(0.7-1.0)

        color = random.choice(['red', 'yellow', 'blue', 'purple'])
        saturation = random.choice(['light', 'muted', 'saturated'])
        brightness = random.choice(['dim', 'moderate', 'bright'])

        self.puzzle_layouts[2] = [color, saturation, brightness]

        return [color,saturation,brightness]


    def wire_puzzle_config(self):
        #KEY:
        #wireNumber: 1(red, straight), 2(red, squiggly), 3(red, zigzag)
        #wireNumber: 4(green, straight), 5(green, squiggly), 6(green, zigzag)
        #wireNumber: 7(blue, straight), 8(blue, squiggly), 9(blue, zigzag)
        #wireNumber: 10(orange, straight), 11(orange, squiggly), 12(orange, zigzag)

        #pick random number of each type of wire
        zigzag_wires = random.randint(0, 4)
        squiggly_wires = random.randint(0, 4 - zigzag_wires)
        straight_wires = 4 - zigzag_wires - squiggly_wires

        straight_nums = [1, 4, 7, 10]
        squiggly_nums = [2, 5, 8, 11]
        zigzag_nums = [3, 6, 9, 12]

        #Select values then randomize order
        selected = []
        selected.extend(random.sample(straight_nums, straight_wires))
        selected.extend(random.sample(squiggly_nums, squiggly_wires))
        selected.extend(random.sample(zigzag_nums, zigzag_wires))
        random.shuffle(selected)

        #save the state for comparison!
        self.puzzle_layouts[0] = [zigzag_wires, squiggly_wires, selected]


    #BROKEN RN
    def solve_led_puzzle(self, color: float, saturation: float, brightness: float):
        #KEY:
        #Colors: red(0.0-0.1), yellow(0.2-0.3), blue(0.5-0.6), purple(0.7-0.8)
        #Saturation: Light(0.0-0.3), Muted(0.4-0.6), Saturated(0.7-1.0)
        #Brightness: Dim(0.0-0.3), Moderate(0.4-0.6), Bright(0.7-1.0)

        if 0.0 <= color <= 0.1:
            chosen_color = 'red'
        elif 0.2 <= color <= 0.3:
            chosen_color = 'yellow'
        elif 0.5 <= color <= 0.6:
            chosen_color = 'blue'
        elif 0.7 <= color <= 0.8:
            chosen_color = 'purple'
        else:
            chosen_color = None

        if 0.0 <= saturation <= 0.3:
            chosen_saturation = 'light'
        elif 0.4 <= saturation <= 0.6:
            chosen_saturation = 'muted'
        elif 0.7 <= saturation <= 1.0:
            chosen_saturation = 'saturated'
        else:
            chosen_saturation = None

        if 0.0 <= brightness <= 0.3:
            chosen_brightness = 'dim'
        elif 0.4 <= brightness <= 0.6:
            chosen_brightness = 'moderate'
        elif 0.7 <= brightness <= 1.0:
            chosen_brightness = 'bright'
        else:
            chosen_brightness = None

        layout = self.puzzle_layouts[2]
        return 1 if (layout[0] == chosen_color and layout[1] == chosen_saturation and layout[2] == chosen_brightness) else 0


    def solve_wire_puzzle(self, positionOfWireCut: int) -> str:
        #KEY:
        #wirePosition: 0, 1, 2, 3
        #wireNumber: 1(red, straight), 2(red, squiggly), 3(red, zigzag)
        #wireNumber: 4(green, straight), 5(green, squiggly), 6(green, zigzag)
        #wireNumber: 7(blue, straight), 8(blue, squiggly), 9(blue, zigzag)
        #wireNumber: 10(orange, straight), 11(orange, squiggly), 12(orange, zigzag)
            

        zigzag_wires = self.puzzle_layouts[0][0]
        squiggly_wires = self.puzzle_layouts[0][1]

        wires = self.puzzle_layouts[0][2]  # assumed: list of wire numbers at positions 0-3

        def color(w):
            if w in (1, 2, 3):   return 'red'
            if w in (4, 5, 6):   return 'green'
            if w in (7, 8, 9):   return 'blue'
            if w in (10, 11, 12): return 'orange'

        def has_color(c):
            return any(color(w) == c for w in wires)

        def first_of_color(c):
            return next((i for i, w in enumerate(wires) if color(w) == c), None)

        def first_squiggly():
            return next((i for i, w in enumerate(wires) if w in (2, 5, 8, 11)), None)

        def first_zigzag():
            return next((i for i, w in enumerate(wires) if w in (3, 6, 9, 12)), None)

        n_sq = squiggly_wires
        n_zz = zigzag_wires
        last = len(wires) - 1

        # Determine the correct wire position to cut
        match (n_sq, n_zz):
            case (0, 0):
                correct = 0 if has_color('red') else last
            case (0, 1):
                correct = first_of_color('green') if has_color('green') else 1
            case (0, 2):
                correct = 0 if has_color('orange') else last
            case (0, 3):
                correct = first_of_color('green') if has_color('green') else 2
            case (0, 4):
                correct = None  # cut any wire
            case (1, 0):
                correct = first_zigzag() if has_color('green') else 1
            case (1, 1):
                correct = None if has_color('blue') else 1  # cut any wire
            case (1, 2):
                correct = first_of_color('green') if has_color('green') else 0
            case (1, 3):
                correct = 0 if has_color('red') else last
            case (2, 0):
                correct = 0 if has_color('orange') else last
            case (2, 1):
                correct = first_of_color('green') if has_color('green') else 0
            case (2, 2):
                correct = None if has_color('blue') else 1  # cut any wire
            case (3, 0):
                correct = first_of_color('green') if has_color('green') else 2
            case (3, 1):
                correct = 0 if has_color('red') else last
            case (4, 0):
                correct = None  # cut any wire
            case _:
                return 0  # undefined state

        # "Cut any wire" — any cut is valid
        if correct is None:
            return 1

        return 1 if positionOfWireCut == correct else 0


#comment out unused puzzle states until they're implemented
    def __init__(self):
        wire_puzzle_layout = self.wire_puzzle_config()
        self.puzzle_codes = [1, 2, 3]
        self.puzzle_algorithms = {
            1: self.solve_wire_puzzle,
            #2: self.solve_puzzle_2,
            #3: self.solve_puzzle_3
        }
        self.puzzle_layouts = []