import random

class Puzzle_Handler:
    puzzle_codes = []
    puzzle_algorithms = {}
    puzzle_layouts = {}


    def solve_puzzle(self, puzzle_code: str) -> str:
        if puzzle_code not in self.puzzle_codes:
            print("Error: puzzle code does not exist!")
            return

    def wire_puzzle_config(self):
        #randomization of squiggly/zigzag first
        #randomization of colors second
        puzzle_state = []

        zigzag_wires = random.randint(0, 4)
        squiggly_wires = random.randint(0, 4 - zigzag_wires)
        colors = []
        count = 0
        while count < 4:
            random_num = random.randint(0, 4)
            colors.append(random_num)
            count += 1

        puzzle_state.append(zigzag_wires)
        puzzle_state.append(squiggly_wires)
        puzzle_state.append(colors)

        self.puzzle_layouts[1] = puzzle_state


    def solve_wire_puzzle(self, positionOfWireCut: int) -> str:
        #KEY:
        #wirePosition: 0, 1, 2, 3
        #wireNumber: 1(red, straight), 2(red, squiggly), 3(red, zigzag)
        #wireNumber: 4(green, straight), 5(green, squiggly), 6(green, zigzag)
        #wireNumber: 7(blue, straight), 8(blue, squiggly), 9(blue, zigzag)
        #wireNumber: 10(orange, straight), 11(orange, squiggly), 12(orange, zigzag)

        zigzag_wires = self.puzzle_layouts[1][0]
        squiggly_wires = self.puzzle_layouts[1][1]

        wires = self.puzzle_layouts[1][2]  # assumed: list of wire numbers at positions 0-3

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


    def __init__(self):
        wire_puzzle_layout = self.wire_puzzle_config()
        self.puzzle_codes = [1, 2, 3]
        self.puzzle_algorithms = {
            1: self.solve_wire_puzzle,
            2: self.solve_puzzle_2,
            3: self.solve_puzzle_3
        }
        self.puzzle_layouts = {
            1: self.wire_puzzle_layout,
            2: self.puzzle_2_layout,
            3: self.puzzle_3_layout
        }