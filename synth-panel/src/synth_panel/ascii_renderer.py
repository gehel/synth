from __future__ import annotations

from synth_panel.dsl import LED, Component, Jack, Panel, Pot, RotarySwitch, ToggleSwitch
from synth_panel.layout import _COMPONENT_SIZE, HP, PlacedComponent, lay_out
from synth_panel.renderer import Renderer

PANEL_ROWS = 52  # character rows for the 128.5mm panel interior
_ROWS_PER_MM = PANEL_ROWS / 128.5
_COLS_PER_MM = _ROWS_PER_MM * 2.0  # terminal chars are ~2:1 tall:wide

_SYMBOL: dict[type[Component], str] = {
    LED: "L",
    Jack: "J",
    Pot: "P",
    ToggleSwitch: "T",
    RotarySwitch: "R",
}


class ASCIIRenderer(Renderer):
    """Renders a panel as an ASCII art string."""

    def render(self, panel: Panel) -> str:  # type: ignore[override]
        placed = lay_out(panel)

        inner_cols = round(panel.width_hp * HP * _COLS_PER_MM)
        total_cols = inner_cols + 2
        total_rows = PANEL_ROWS + 2

        grid = [[" "] * total_cols for _ in range(total_rows)]

        self._draw_border(grid, total_rows, total_cols)

        for pc in placed:
            self._draw_component(pc, grid, total_rows, total_cols)

        return "\n".join("".join(row) for row in grid)

    def _draw_border(self, grid: list[list[str]], total_rows: int, total_cols: int) -> None:
        for c in range(total_cols):
            grid[0][c] = "-"
            grid[total_rows - 1][c] = "-"
        for r in range(total_rows):
            grid[r][0] = "|"
            grid[r][total_cols - 1] = "|"
        grid[0][0] = "+"
        grid[0][total_cols - 1] = "+"
        grid[total_rows - 1][0] = "+"
        grid[total_rows - 1][total_cols - 1] = "+"

    def _draw_component(
        self,
        pc: PlacedComponent,
        grid: list[list[str]],
        total_rows: int,
        total_cols: int,
    ) -> None:
        row = round(pc.y * _ROWS_PER_MM) + 1
        col = round(pc.x * _COLS_PER_MM) + 1

        size_mm = _COMPONENT_SIZE[type(pc.component)]
        half_h = max(1, round(size_mm * _ROWS_PER_MM / 2))
        half_w = 3  # fixed horizontal half-width in chars

        r1 = row - half_h
        r2 = row + half_h
        c1 = col - half_w
        c2 = col + half_w

        def in_bounds(r: int, c: int) -> bool:
            return 0 < r < total_rows - 1 and 0 < c < total_cols - 1

        # Box outline
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if not in_bounds(r, c):
                    continue
                if r in (r1, r2):
                    grid[r][c] = "-"
                elif c in (c1, c2):
                    grid[r][c] = "|"

        # Type symbol at center
        if in_bounds(row, col):
            grid[row][col] = _SYMBOL[type(pc.component)]

        # Label one row above center (inside box if it fits)
        label = pc.component.label or ""
        if label:
            label_row = row - 1 if row - 1 > r1 else row + 1
            label_start = col - len(label) // 2
            max_len = 2 * half_w - 1
            for i, ch in enumerate(label[:max_len]):
                c = label_start + i
                if in_bounds(label_row, c):
                    grid[label_row][c] = ch
