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

        return puzzle_state


    def solve_wire_puzzle(self, wireCut: int, wirePosition: int) -> str:
        #KEY:
        #wirePosition: 0, 1, 2, 3
        #wireNumber: 1(red, straight), 2(red, squiggly), 3(red, zigzag)
        #wireNumber: 4(green, straight), 5(green, squiggly), 6(green, zigzag)
        #wireNumber: 7(blue, straight), 8(blue, squiggly), 9(blue, zigzag)
        #wireNumber: 10(orange, straight), 11(orange, squiggly), 12(orange, zigzag)

        zigzag_wires = self.puzzle_layouts[1][0]
        squiggly_wires = self.puzzle_layouts[1][1]


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