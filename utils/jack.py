# This is a sample Python script.
from math import cos, pi, sin
from typing import Tuple
from KicadModTree import Circle, Footprint, KicadFileHandler


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def potentiometer_panel():
    kicad_mod = Footprint('jack')

    kicad_mod.append(Circle(center=[0, 6.48], radius=3.2, layer='Edge.Cuts'))

    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile('{name}.kicad_mod'.format(name='jack'))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    potentiometer_panel()
