# This is a sample Python script.
from math import cos, pi, sin
from typing import Tuple
from KicadModTree import Circle, Footprint, KicadFileHandler, Line, Text, Translation


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def potentiometer_panel():
    kicad_mod = Footprint('Potentiometer dial')

    translation = Translation(7, -2.5)
    kicad_mod.append(translation)

    translation.append(Circle(center=[0, 0], radius=3.1, layer='Edge.Cuts'))

    for polar in sequence_of_polar_coord(5, increment=2*pi/48, start=pi / 6, end=11 * pi / 6):
        translation.append(Line(start=[0, 0], end=polar_to_cartesian(*polar), width=0.1))

    for polar in sequence_of_polar_coord(5.5, increment=2*pi/12, start=pi / 6, end=11 * pi / 6):
        translation.append(Line(start=[0, 0], end=polar_to_cartesian(*polar), width=0.1))

    n = 0
    for polar in sequence_of_polar_coord(6, increment=2*pi/12, start=pi / 6, end=11 * pi / 6):
        cartesian = polar_to_cartesian(*polar)
        translation.append(Text(type='user', at=(cartesian[0] + 0, cartesian[1] + 0), text=n, rotation=90))
        n = n+1


    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile('{name}.kicad_mod'.format(name='potentiometer_dial'))


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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    potentiometer_panel()
