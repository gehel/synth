from __future__ import annotations

from kipy.geometry import Vector2
from kipy.kicad import KiCad

from synth_panel.dsl import Panel
from synth_panel.layout import PlacedComponent, lay_out
from synth_panel.renderer import Renderer


class PcbRenderer(Renderer):
    """Moves footprints on the open KiCad PCB to the computed layout positions.

    Prerequisite: the schematic has been generated and the user has clicked
    "Update PCB from Schematic" in KiCad to place all footprints on the board.

    :param origin_x_mm: X offset in mm from KiCad PCB origin to the panel top-left corner.
    :param origin_y_mm: Y offset in mm from KiCad PCB origin to the panel top-left corner.
    """

    def __init__(self, origin_x_mm: float = 0.0, origin_y_mm: float = 0.0) -> None:
        self._origin_x_mm = origin_x_mm
        self._origin_y_mm = origin_y_mm

    def render(self, panel: Panel) -> None:
        placed = lay_out(panel)
        ref_map: dict[str, PlacedComponent] = {pc.reference: pc for pc in placed}

        kicad = KiCad()
        board = kicad.get_board()

        to_update = []
        for fp in board.get_footprints():
            ref = fp.reference_field.text.value
            pc = ref_map.get(ref)
            if pc is None:
                continue
            fp.position = Vector2.from_xy_mm(
                self._origin_x_mm + pc.x,
                self._origin_y_mm + pc.y,
            )
            to_update.append(fp)

        if not to_update:
            return

        commit = board.begin_commit()
        try:
            board.update_items(to_update)
            board.push_commit(commit, f"Place {panel.name} components")
        except Exception:
            board.drop_commit(commit)
            raise