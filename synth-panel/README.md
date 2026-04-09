# synth-panel

A Python tool for generating KiCad v9 projects for Eurorack modular synthesizer panels.

Describe your panel using a Python DSL — components, labels, and layout — and get two KiCad projects ready to send to a fab:

1. **Main PCB** — holds the components with all electrical traces
2. **Front panel PCB** — an aluminium PCB with only holes and silkscreen labels, sized and aligned so components poke through from the main PCB behind it

## Features

- Class-based DSL for describing panel layout
- Supports common Eurorack panel components: jacks, potentiometers, toggle switches, rotary switches, LEDs
- Horizontal and vertical section layout
- Automatic label placement on the front panel
- Generates two complete KiCad v9 projects (`.kicad_pcb`, `.kicad_sch`, `.kicad_pro`)
- Hole positions on the front panel are automatically aligned to component positions on the main PCB
- Uses footprints and symbols from the project's own KiCad library

## Requirements

- Python 3.13+
- [Poetry](https://python-poetry.org/) for dependency management
- KiCad v9 (for viewing/editing generated files)

## Installation

```bash
git clone <repo-url>
cd synth-panel
poetry install
```

## Usage

```python
from synth_panel import Panel, Section, Jack, Pot, ToggleSwitch, LED

panel = Panel(
    name="VCF",
    width_hp=8,
    sections=[
        Section(label="Input", components=[
            Jack(label="Audio In"),
            Jack(label="CV"),
        ]),
        Section(label="Controls", components=[
            Pot(label="Cutoff"),
            Pot(label="Resonance"),
            ToggleSwitch(label="Mode"),
        ]),
        Section(label="Output", components=[
            Jack(label="Audio Out"),
            LED(label="Signal"),
        ]),
    ]
)

panel.write("output/VCF")
```

This produces two KiCad projects:

- `output/VCF/pcb/` — main PCB with components and traces
- `output/VCF/panel/` — aluminium front panel PCB with holes and labels

## Panel format

Eurorack panels follow the [Doepfer A-100 mechanical standard](https://www.doepfer.de/a100_man/a100m_e.htm):

- Panel height: 128.5 mm (3U)
- Width in HP (1 HP = 5.08 mm)
- Mounting holes at standard positions

## Component library

Footprints and symbols are sourced from `../Library.pretty/` and `../Synth.kicad_sym` relative to this repository. These include:

- `Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles` — 3.5mm mono jack
- `Potentiometer_Bourns_PTV09A-1_Single_Vertical` — 9mm single pot
- `Potentiometer_Alpha_RD902F-40-00D_Dual_Vertical` — 9mm dual pot
- `ToggleSwitch_MTS-102_SPDT` — SPDT toggle switch
- `rotary_switch_1P12T`, `rotary_switch_3P4T` — rotary switches

## License

Apache License 2.0 — see [LICENSE](LICENSE).