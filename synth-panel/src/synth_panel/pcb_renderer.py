from __future__ import annotations

import re

from kipy.board import Board
from kipy.board_types import BoardLayer, BoardRectangle
from kipy.geometry import Vector2, from_mm
from kipy.kicad import KiCad

from synth_panel.dsl import Panel
from synth_panel.layout import HP, PANEL_HEIGHT, PlacedComponent, lay_out
from synth_panel.renderer import Renderer

_OUTLINE_STROKE_MM = 0.05

# KiCad paper sizes in mm: (width, height) in landscape orientation.
_PAPER_SIZES_MM: dict[str, tuple[float, float]] = {
    "A4": (297.0, 210.0),
    "A3": (420.0, 297.0),
    "A2": (594.0, 420.0),
    "A1": (841.0, 594.0),
    "A0": (1189.0, 841.0),
    "Letter": (279.4, 215.9),
    "Legal": (355.6, 215.9),
    "Ledger": (431.8, 279.4),
}


class PcbRenderer(Renderer):
    """Moves footprints on the open KiCad PCB to the computed layout positions,
    draws the Eurorack board outline on Edge.Cuts, and centers the board on the sheet.

    Prerequisite: the schematic has been generated and the user has clicked
    "Update PCB from Schematic" in KiCad to place all footprints on the board.
    """

    def render(self, panel: Panel) -> None:
        placed = lay_out(panel)
        ref_map: dict[str, PlacedComponent] = {pc.reference: pc for pc in placed}

        kicad = KiCad()
        board = kicad.get_board()

        origin_x, origin_y = self._centered_origin(board, panel)

        to_update = []
        for fp in board.get_footprints():
            ref = fp.reference_field.text.value
            pc = ref_map.get(ref)
            if pc is None:
                continue
            fp.position = Vector2.from_xy_mm(origin_x + pc.x, origin_y + pc.y)
            to_update.append(fp)

        existing_outline = [s for s in board.get_shapes() if s.layer == BoardLayer.BL_Edge_Cuts]
        outline = self._build_outline(panel, origin_x, origin_y)

        if not to_update and not existing_outline:
            return

        commit = board.begin_commit()
        try:
            if to_update:
                board.update_items(to_update)
            if existing_outline:
                board.remove_items(existing_outline)
            board.create_items([outline])
            board.push_commit(commit, f"Place {panel.name} components")
        except Exception:
            board.drop_commit(commit)
            raise

    def _centered_origin(self, board: Board, panel: Panel) -> tuple[float, float]:
        """Return the top-left origin (mm) that centers the panel on the sheet."""
        sheet_w, sheet_h = self._sheet_size_mm(board)
        panel_w = panel.width_hp * HP
        return (sheet_w - panel_w) / 2, (sheet_h - PANEL_HEIGHT) / 2

    def _sheet_size_mm(self, board: Board) -> tuple[float, float]:
        text = board.get_as_string()
        match = re.search(r'\(paper "([^"]+)"', text)
        if match:
            size = _PAPER_SIZES_MM.get(match.group(1))
            if size:
                return size
        return _PAPER_SIZES_MM["A4"]

    def _build_outline(self, panel: Panel, origin_x: float, origin_y: float) -> BoardRectangle:
        width_mm = panel.width_hp * HP
        rect = BoardRectangle()
        rect.layer = BoardLayer.BL_Edge_Cuts
        rect.top_left = Vector2.from_xy_mm(origin_x, origin_y)
        rect.bottom_right = Vector2.from_xy_mm(origin_x + width_mm, origin_y + PANEL_HEIGHT)
        rect.attributes.stroke.width = from_mm(_OUTLINE_STROKE_MM)
        return rect