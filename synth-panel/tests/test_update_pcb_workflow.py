"""Manual workflow test: schematic → KiCad → "Update PCB from Schematic" → place footprints.

Excluded from the standard test suite (requires a running KiCad instance).
Run explicitly with:

    poetry run pytest -m manual tests/test_update_pcb_workflow.py -s

Steps performed automatically:
  1. Generate the KiCad project (schematic + blank PCB) in output/manual_pcb_workflow/
  2. Launch KiCad and open the project.

Steps you must perform manually in KiCad:
  3. Open the PCB editor (Tools → Open PCB in Board Editor, or double-click the .kicad_pcb).
  4. Click Tools → "Update PCB from Schematic…" (F8) and press "Update PCB".
  5. Close or minimise KiCad (the PCB editor may stay open — that is fine).
  6. Press Enter in this terminal.

Steps performed automatically after you press Enter:
  7. Connect to the running KiCad instance via the scripting API and move every
     footprint to its computed panel position.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from synth_panel import (
    LED,
    Jack,
    KicadProject,
    Panel,
    Pot,
    RotarySwitch,
    SchematicRenderer,
    Section,
    ToggleSwitch,
)
from synth_panel.pcb_renderer import PcbRenderer

OUTPUT_DIR = Path(__file__).parent.parent / "output"
PANEL_NAME = "manual_pcb_workflow"


def _panel() -> Panel:
    return Panel(
        name=PANEL_NAME,
        width_hp=8,
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


def _find_kicad() -> str:
    candidates = [
        "kicad",
        "/snap/bin/kicad",
        "/usr/bin/kicad",
        "/usr/local/bin/kicad",
    ]
    for cmd in candidates:
        if subprocess.run(["which", cmd], capture_output=True).returncode == 0:
            return cmd
        if Path(cmd).exists():
            return cmd
    return "kicad"


def _generate_schematic(panel: Panel, project: KicadProject) -> Path:
    print(f"\nGenerating schematic in {project.project_dir} …")
    SchematicRenderer(project).render(panel)
    project_file = project.project_dir / f"{PANEL_NAME}.kicad_pro"
    print(f"Project written to: {project_file}")
    return project_file


def _open_kicad(project_file: Path) -> None:
    cmd = [_find_kicad(), str(project_file)]
    print(f"Launching KiCad: {' '.join(cmd)}")
    subprocess.Popen(cmd)


def _wait_for_update_pcb() -> None:
    print()
    print("=" * 60)
    print("KiCad is now open.")
    print()
    print("Please do the following inside KiCad:")
    print("  1. Switch to the PCB editor")
    print('     (Tools → "Open PCB in Board Editor")')
    print("  2. Click  Tools → 'Update PCB from Schematic…'  (F8)")
    print('  3. In the dialog, click "Update PCB"')
    print("  4. Close the dialog (the footprints will appear unplaced)")
    print()
    print("When done, come back here and press Enter.")
    print("=" * 60)
    input()


def _place_footprints(panel: Panel) -> None:
    print("Placing footprints on the open PCB …")
    PcbRenderer().render(panel)
    print("Done! Footprints have been placed.")
    print()
    print("You can now inspect the result in the KiCad PCB editor.")


@pytest.mark.manual
def test_update_pcb_workflow(pytestconfig):
    panel = _panel()
    project = KicadProject(OUTPUT_DIR / PANEL_NAME)

    project_file = _generate_schematic(panel, project)
    _open_kicad(project_file)
    _wait_for_update_pcb()
    _place_footprints(panel)