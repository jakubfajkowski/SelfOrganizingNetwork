import time
import colorsys


def millis():
    return int(round(time.time() * 1000))


COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_LIGHT_GREY = (192, 192, 192)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)

WINDOW_SIZE = 600
DEFAULT_SPEED = 100
CENTER_POINT = (WINDOW_SIZE/2, WINDOW_SIZE/2)

POWER_DENSITY_THRESHOLD = 1
