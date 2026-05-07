import pigpio
import time

class LosingSequence:
    def __init__(self):
        self.pi1 = pigpio.pi()
        blue = self.blue
        red = self.red
        green = self.green
        self.pi1.write(blue, 0)
        self.pi1.write(red, 0)
        self.pi1.write(green,0)

    def run(self):

        try:
            # run forever when connected
            while True:
                # Turn off all LEDs
                self.pi1.write(self.blue, 0)
                self.pi1.write(self.red, 0)
                self.pi1.write(self.green,0)

                # Delay 1 second
                time.sleep(0.25)
    
                self.pi1.write(red,1)
                time.sleep(0.5)

        except KeyboardInterrupt: # ctrl C exit
            # Turn off all LEDs before exiting
            self.stop()

    def stop(self):
        self.pi1.write(self.blue, 0)
        self.pi1.write(self.red, 0)
        self.pi1.write(self.green,0)
        self.pi1.stop()
