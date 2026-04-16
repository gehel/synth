"""Integration test for PcbRenderer.

Verifies that every footprint lands at the position computed by ``lay_out``
after ``PcbRenderer.render()`` is called against a live KiCad instance.

Prerequisites
-------------
1. Generate the schematic (idempotent, safe to re-run)::

       poetry run pytest tests/test_sch_renderer.py::test_render_schematic_manual_inspection

2. Open the resulting PCB in KiCad::

       output/manual_inspection/manual_inspection.kicad_pcb

3. Inside the PCB editor, populate footprints:
   Tools → "Update PCB from Schematic…" → "Update PCB" → Close dialog.

4. Run this test (KiCad must remain open)::

       poetry run pytest -m manual tests/test_pcb_renderer.py -s
"""

from __future__ import annotations

import pytest

from kipy.geometry import from_mm
from kipy.kicad import KiCad

from synth_panel import (
    LED,
    Jack,
    Panel,
    Pot,
    RotarySwitch,
    Section,
    ToggleSwitch,
)
from synth_panel.layout import lay_out
from synth_panel.pcb_renderer import PcbRenderer

ORIGIN_X_MM = 0.0
ORIGIN_Y_MM = 0.0

# Allow 1 nm of rounding error from the mm→nm integer conversion.
TOLERANCE_NM = 1


def _panel() -> Panel:
    return Panel(
        name="manual_inspection",
        width_hp=10,
        sections=[
            Section(
                components=[
                    Jack(label="IN"),
                    Pot(label="CUTOFF"),
                    Pot(label="RESONANCE"),
                    ToggleSwitch(label="MODE"),
                    RotarySwitch(label="RANGE", poles=1, throws=12),
                    LED(label="CLIP"),
                    Jack(label="OUT"),
                ]
            )
        ],
    )


@pytest.mark.manual
def test_pcb_renderer_places_footprints_at_computed_positions():
    """PcbRenderer must move every footprint to the position returned by lay_out."""
    panel = _panel()
    expected = {pc.reference: pc for pc in lay_out(panel)}

    PcbRenderer(origin_x_mm=ORIGIN_X_MM, origin_y_mm=ORIGIN_Y_MM).render(panel)

    board = KiCad().get_board()
    footprints = board.get_footprints()

    board_refs = {fp.reference_field.text.value for fp in footprints}
    missing = set(expected) - board_refs
    assert not missing, f"Footprints not found on board: {missing}"

    mismatches = []
    for fp in footprints:
        ref = fp.reference_field.text.value
        pc = expected.get(ref)
        if pc is None:
            continue

        want_x = from_mm(ORIGIN_X_MM + pc.x)
        want_y = from_mm(ORIGIN_Y_MM + pc.y)
        got_x = fp.position.x
        got_y = fp.position.y

        if abs(got_x - want_x) > TOLERANCE_NM or abs(got_y - want_y) > TOLERANCE_NM:
            mismatches.append(
                f"  {ref}: expected ({want_x} nm, {want_y} nm) "
                f"got ({got_x} nm, {got_y} nm)"
            )

    assert not mismatches, "Footprint position mismatches:\n" + "\n".join(mismatches)