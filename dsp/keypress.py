import time
import random
from pynput.keyboard import Controller, Key

keyboard = Controller()  # Create the controller

for i in range(10):
    time.sleep(random.randint(0, 1))
    keyboard.press(Key.space)
    keyboard.release(Key.space)

