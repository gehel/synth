from math import pi

from KicadModTree import Circle, Footprint, KicadFileHandler, Line, Text, Translation, Pad

from coord import polar_to_cartesian, sequence_of_polar_coord


def rotary_switch():
    kicad_mod = Footprint('Potentiometer dial')

    pad_num = 1
    for polar in sequence_of_polar_coord(22.2 / 2, increment=2 * pi / 12, start=2 * pi / 24, end=23 * 2 * pi / 24):
        kicad_mod.append(Pad(number=pad_num, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, at=polar_to_cartesian(*polar),
                             size=1.8, drill=1.1, layers=Pad.LAYERS_THT))
        pad_num += 1

    for polar in sequence_of_polar_coord(7.7 / 2, increment=2 * pi / 4, start=2 * pi / 8, end=7 * 2 * pi / 8):
        kicad_mod.append(Pad(number=pad_num, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE, at=polar_to_cartesian(*polar),
                             size=1.8, drill=1.1, layers=Pad.LAYERS_THT))
        pad_num += 1

    kicad_mod.append(Circle(center=[0, 0], radius=26.19/2, layer='F.SilkS'))
    kicad_mod.append(Circle(center=[0, 0], radius=26.19/2 + 0.5, layer='F.CrtYd'))

    file_handler = KicadFileHandler(kicad_mod)
    file_handler.writeFile('{name}.kicad_mod'.format(name='rotary_switch_1P12T'))


if __name__ == '__main__':
    rotary_switch()