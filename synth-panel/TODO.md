# TODO

## In progress

## Backlog

### Wire up missing footprints
`ToggleSwitch`, `RotarySwitch`, and `LED` all return `UNKNOWN_FOOTPRINT`.
Real footprints are already in `../Library.pretty/`:
- `ToggleSwitch` → `ToggleSwitch_MTS-102_SPDT.kicad_mod`
- `RotarySwitch(1, 12)` → `rotary_switch_1P12T.kicad_mod`
- `RotarySwitch(3, 4)` → `rotary_switch_3P4T.kicad_mod`
- `LED` → pick or add an appropriate THT LED footprint

Unblocks: integration test (SW1, SW2, D1 currently missing from board).

### Front panel PCB generator
CLAUDE.md describes a second output path: an aluminium panel PCB with
drilled holes and silkscreen labels, no copper traces.  Not yet implemented.
- Map each component to its panel-hole footprint variant
  (e.g. `Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles-panel.kicad_mod`,
  `MTS-102 panel hole.kicad_mod`)
- Place silkscreen labels next to each hole
- Add `Edge.Cuts` board outline sized to the panel's HP width × 128.5 mm

### ~~Board outline (Edge.Cuts) on the main PCB~~ ✓ Done

### Eurorack mounting holes
Standard Eurorack panels require 3.2 mm mounting holes at fixed positions
(top and bottom, inset 3 mm from the rail edge).  Neither PCB output places
these yet.

### Dual pot support
`Potentiometer_Alpha_RD902F-40-00D_Dual_Vertical.kicad_mod` is in the
library but there is no `DualPot` DSL component.

### Automate "Update PCB from Schematic"
The current workflow requires the user to click F8 in KiCad by hand.
Investigate whether `kicad-cli` or the IPC API's `run_action` can trigger
this step programmatically so the full pipeline can be scripted end-to-end.

### Complete the integration test
`test_pcb_renderer.py::test_pcb_renderer_places_footprints_at_computed_positions`
currently fails because SW1, SW2, D1 are absent from the board (missing
footprints, see above).  Once footprints are wired up, re-run the full
manual workflow and verify the test passes.

### Misc
* [ ] add optional outline to sections
* [ ] add optional titles to sections
* [ ] add IDs to components and sections to ensure that we can update the
boards / schematic after changes (store that ID in a custom field in Kicad)

### README
Update `README.md` to document the two-project output (main PCB + front panel),
the manual workflow steps, and the `manual` pytest marker.