from math import cos, sin


def sequence_of_polar_coord(radius: float, increment: float, start: float, end: float):
    n = 0
    while True:
        angle = start + n * increment
        n = n + 1
        if angle > end:
            break
        yield radius, angle


def polar_to_cartesian(radius: float, angle: float):
    return cos(angle) * radius, sin(angle) * radius
