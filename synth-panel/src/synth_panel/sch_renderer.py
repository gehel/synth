from __future__ import annotations

import shutil
import warnings
from pathlib import Path
from typing import Optional

import kicad_sch_api as ksa

from synth_panel.dsl import LED, Component, Jack, Panel, Pot, RotarySwitch, ToggleSwitch
from synth_panel.layout import PlacedComponent, lay_out
from synth_panel.renderer import Renderer

# Known KiCad symbol library locations (checked in order).
_KICAD_SYMBOL_DIRS: list[Path] = [
    Path("/snap/kicad/current/usr/share/kicad/symbols"),  # snap
    Path("/usr/share/kicad/symbols"),  # system package
    Path("/usr/local/share/kicad/symbols"),  # manual install
    Path.home() / ".var/app/org.kicad.KiCad/data/kicad/9.0/symbols",  # flatpak
]

# Mapping from DSL component type → KiCad symbol lib_id
_LIB_ID: dict[type[Component], str] = {  # noqa: UP006
    Jack: "Connector_Audio:AudioJack2",
    Pot: "Device:R_Potentiometer_MountingPin",
    ToggleSwitch: "Switch:SW_SPDT",
    LED: "Device:LED",
}

# RotarySwitch lib_id depends on poles/throws — resolved at render time
_ROTARY_LIB_ID: dict[tuple[int, int], str] = {
    (1, 12): "Switch:SW_Rotary_1x12",
    (3, 4): "Switch:SW_Rotary_3x4",
}

# Reference designator prefix per component type
_REF_PREFIX: dict[type[Component], str] = {  # noqa: UP006
    Jack: "J",
    Pot: "RV",
    ToggleSwitch: "SW",
    RotarySwitch: "SW",
    LED: "D",
}

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

        # Track per-prefix counters for reference designators
        counters: dict[str, int] = {}

        for pc in placed:
            comp_type = type(pc.component)
            prefix = _REF_PREFIX[comp_type]
            counters[prefix] = counters.get(prefix, 0) + 1
            ref = f"{prefix}{counters[prefix]}"
            value = pc.component.label or comp_type.__name__
            grid_x = round(pc.x / _GRID_MM)
            grid_y = round(pc.y / _GRID_MM)

            if isinstance(pc.component, RotarySwitch):
                key = (pc.component.poles, pc.component.throws)
                lib_id = _ROTARY_LIB_ID.get(key)
                if lib_id is None:
                    raise ValueError(
                        f"No KiCad symbol for RotarySwitch "
                        f"poles={pc.component.poles}, throws={pc.component.throws}. "
                        f"Supported: {list(_ROTARY_LIB_ID.keys())}"
                    )
            else:
                lib_id = _LIB_ID[comp_type]

            sch.components.add(
                lib_id,
                reference=ref,
                value=value,
                position=(grid_x, grid_y),
            )

        sch.save(str(sch_path))
