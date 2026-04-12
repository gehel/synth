from __future__ import annotations

import shutil
import warnings
from pathlib import Path
from typing import Optional

import kicad_sch_api as ksa

from synth_panel.dsl import Panel
from synth_panel.layout import PlacedComponent, lay_out
from synth_panel.renderer import Renderer
from synth_panel.sch_component_factory import SchematicComponentFactory

_KICAD_SYMBOL_DIRS: list[Path] = [
    Path("/snap/kicad/current/usr/share/kicad/symbols"),  # snap
    Path("/usr/share/kicad/symbols"),  # system package
    Path("/usr/local/share/kicad/symbols"),  # manual install
    Path.home() / ".var/app/org.kicad.KiCad/data/kicad/9.0/symbols",  # flatpak
]

_TEMPLATE_DIR = Path(__file__).parent / "template" / "blank"
_GRID_MM = 1.27  # mm per KiCad grid unit (50 mil)


class SchematicRenderer(Renderer):
    """Renders a panel as a KiCad schematic project."""

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir

    def render(self, panel: Panel) -> None:
        placed = lay_out(panel)
        self._configure_symbol_libraries()
        self._write_schematic(panel, placed, self._output_dir / panel.name)


    def _configure_symbol_libraries(self) -> None:
        """Point kicad-sch-api at the system KiCad symbol libraries."""
        cache = ksa.get_symbol_cache()
        for path in _KICAD_SYMBOL_DIRS:
            if path.exists():
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    cache.discover_libraries([str(path)])
                return
        raise RuntimeError(
            "KiCad symbol libraries not found. "
            "Set KICAD_SYMBOL_DIR or install KiCad."
        )


    def _write_schematic(self, panel: Panel, placed: list[PlacedComponent], dest: Path) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        sch_path = dest / f"{panel.name}.kicad_sch"

        # Copy all blank template files as starting point
        for suffix in (".kicad_sch", ".kicad_pro", ".kicad_pcb", ".kicad_prl"):
            shutil.copy(_TEMPLATE_DIR / f"blank{suffix}", dest / f"{panel.name}{suffix}")

        ksa.use_grid_units(True)
        sch = ksa.load_schematic(str(sch_path))

        factory = SchematicComponentFactory()
        for pc in placed:
            sch_component = factory.create(pc.component)
            value = pc.component.label or type(pc.component).__name__
            grid_x = round(pc.x / _GRID_MM)
            grid_y = round(pc.y / _GRID_MM)
            sch_component.add_to_schematic(sch, value, grid_x, grid_y)

        sch.save(str(sch_path))
