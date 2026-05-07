import pigpio
import time

# this is the winning sequence that happens if you WIN the game
# by successfully the solving all of the puzzles in time

class WinningSequence:
    def __init__(self):
        self.pi1 = pigpio.pi()
        self.blue = 13
        self.red = 19
        self.green = 26

    def run(self):
        try:
            # run forever when connected
            while True:
                # Turn off all LEDs
                self.pi1.write(blue, 0)
                self.pi1.write(red, 0)
                self.pi1.write(green,0)

            # Delay 1 second
                self.time.sleep(0.25)
    
                self.pi1.write(green,1)
                self.time.sleep(0.5)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        # Turn off all LEDs before exiting
        self.pi1.write(blue, 0)
        self.pi1.write(red, 0)
        self.pi1.write(green,0)
        self.pi1.stop()
