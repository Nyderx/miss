from utils import DAY_TIME
from math import cos, sin, pi

import random

step = 2 * pi / DAY_TIME


def standard_function(time, func):
    time_of_day = time % DAY_TIME

    probability = func(step * time_of_day) * 100

    if random.randint(0, 100) < probability:
        return True


def standard_center_function(time):
    return standard_function(time, cos)

def standard_suburbs_function(time):
    return standard_function(time, sin)


