from __future__ import annotations

import warnings
from pathlib import Path

import kicad_sch_api as ksa

from synth_panel.dsl import Panel
from synth_panel.kicad_project import KicadProject
from synth_panel.layout import PlacedComponent, lay_out
from synth_panel.renderer import Renderer

_KICAD_SYMBOL_DIRS: list[Path] = [
    Path("/snap/kicad/current/usr/share/kicad/symbols"),  # snap
    Path("/usr/share/kicad/symbols"),  # system package
    Path("/usr/local/share/kicad/symbols"),  # manual install
    Path.home() / ".var/app/org.kicad.KiCad/data/kicad/9.0/symbols",  # flatpak
]

_GRID_MM = 1.27  # mm per KiCad grid unit (50 mil)


class SchematicRenderer(Renderer):
    """Renders a panel as a KiCad schematic project."""

    def __init__(self, project: KicadProject) -> None:
        self._project = project

    def render(self, panel: Panel) -> None:
        placed = lay_out(panel)
        self._configure_symbol_libraries()
        self._project.init_project()
        self._write_schematic(placed)

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
            "KiCad symbol libraries not found. Set KICAD_SYMBOL_DIR or install KiCad."
        )

    def _write_schematic(self, placed: list[PlacedComponent]) -> None:
        sch_path = self._project.project_dir / f"{self._project.name}.kicad_sch"

        ksa.use_grid_units(True)
        sch = ksa.load_schematic(str(sch_path))

        existing_refs = {c.reference for c in sch.components.filter()}
        for pc in placed:
            if pc.reference in existing_refs:
                continue
            grid_x = round(pc.x / _GRID_MM)
            grid_y = round(pc.y / _GRID_MM)
            pc.component.add_to_schematic(sch, pc.reference, grid_x, grid_y)

        sch.save(str(sch_path))
