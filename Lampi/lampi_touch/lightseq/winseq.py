import pigpio
import time

# this is the winning sequence that happens if you WIN the game
# by successfully the solving all of the puzzles in time

# pins
pi1 = pigpio.pi()
blue = 13
red = 19
green = 26

try:
    # run forever when connected
    while True:
        # Turn off all LEDs
        pi1.write(blue, 0)
        pi1.write(red, 0)
        pi1.write(green,0)

        # Delay 1 second
        time.sleep(0.25)

        pi1.write(green,1)
        time.sleep(0.5)

except KeyboardInterrupt: # ctrl C exit
    # Turn off all LEDs before exiting
    pi1.write(blue, 0)
    pi1.write(red, 0)
    pi1.write(green,0)
    pi1.stop()
