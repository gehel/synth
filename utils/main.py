# This is a sample Python script.
from math import cos, pi, sin
from typing import Tuple
from KicadModTree import Circle, Footprint, KicadFileHandler, Line


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def potentiometer_panel(radius: float, n: int, offset: Tuple[float, float] = (0, 0)):
    kicad_mod = Footprint('potentiometer_panel')
    kicad_mod.append(Circle(center=[0, 0], radius=radius, layer='Edge.Cuts'))

    for end in polar_to_cartesian(5, 12*4, valid_from=pi/6, valid_to=pi/6*11):
        kicad_mod.append(Line(start=[0, 0], end=end, width=0.1))

    for end in polar_to_cartesian(7, 12, valid_from=pi/6, valid_to=pi/6*11):
        kicad_mod.append(Line(start=[0, 0], end=end, width=0.2))

    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile('{name}.kicad_mod'.format(name='potentiometer_panel'))


def polar_to_cartesian(radius, n, valid_from=0, valid_to=2*pi, offset: Tuple[float, float] = (0, 0)):
    for i in range(n):
        angle = 2 * pi / n * i
        if valid_from <= angle <= valid_to:
            yield [
                cos(angle) * radius + offset[0],
                sin(angle) * radius + offset[1]
            ]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    potentiometer_panel(8, 12, (-0.45, 0.6))
