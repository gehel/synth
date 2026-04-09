# CLAUDE.md

## Project overview

`synth-panel` generates KiCad v9 projects for Eurorack modular synthesizer panels. The user describes a panel via a Python DSL and the tool produces a complete KiCad project (PCB + schematic + project file).

## Key decisions

- **Target format**: Eurorack (Doepfer A-100 standard), 3U height (128.5 mm), width in HP (1 HP = 5.08 mm)
- **KiCad version**: v9
- **Output**: Two KiCad projects from a single DSL description:
  1. **Main PCB** (`output/<name>/pcb/`) — standard PCB with components mounted and electrical traces
  2. **Front panel PCB** (`output/<name>/panel/`) — aluminium PCB with no traces, only drilled holes and silkscreen labels; hole positions are aligned to the component positions on the main PCB so components poke through
- **DSL style**: Class-based Python (not builder or dict-based)
- **Python**: 3.13+, managed with Poetry
- **License**: Apache 2.0
- **Author**: Guillaume Lederrey <guillaume.lederrey@gmail.com>

## Repository layout

```
synth-panel/           # this repo
  src/synth_panel/     # main package
  tests/               # pytest tests
  pyproject.toml
  CLAUDE.md
  README.md
  LICENSE

../Library.pretty/     # KiCad footprint library (sibling directory)
../Synth.kicad_sym     # KiCad symbol library (sibling file)
```

## KiCad component library

Footprints live in `../Library.pretty/` (relative to repo root). Key panel-relevant footprints:

| Footprint file | Use |
|---|---|
| `Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles-panel.kicad_mod` | 3.5mm jack (panel hole variant) |
| `Potentiometer_Bourns_PTV09A-1_Single_Vertical-panel.kicad_mod` | Single 9mm pot (panel hole variant) |
| `Potentiometer_Alpha_RD902F-40-00D_Dual_Vertical.kicad_mod` | Dual 9mm pot |
| `ToggleSwitch_MTS-102_SPDT.kicad_mod` | SPDT toggle switch |
| `MTS-102 panel hole.kicad_mod` | Toggle switch panel hole |
| `rotary_switch_1P12T.kicad_mod` | 1-pole 12-throw rotary switch |
| `rotary_switch_3P4T.kicad_mod` | 3-pole 4-throw rotary switch |

Symbols live in `../Synth.kicad_sym`.

## DSL design intent

The DSL describes panels declaratively. Panels contain `Section`s (horizontal or vertical), which contain components. Components carry labels and type-specific parameters (e.g., pot taper, jack signal direction).

The generator has two output paths from the same DSL:

- **Main PCB generator**: maps each component to its full KiCad footprint + schematic symbol, computes positions, adds electrical traces, and emits a KiCad project.
- **Front panel generator**: maps each component to a panel-hole footprint (or just a drill hit + courtyard), places silkscreen labels, and emits a separate KiCad project sized to the Eurorack panel dimensions. No electrical layers are used.

Hole positions on the front panel must exactly match component body positions on the main PCB — the layout engine computes positions once and uses them for both outputs.

## Development

```bash
poetry install
poetry run pytest
```

## Testing

Use pytest. Tests should cover DSL construction and KiCad output generation. Avoid mocking KiCad file I/O where possible — prefer generating to a temp directory and asserting on file content.