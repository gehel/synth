import pytest

from synth_panel import (
    LED,
    Component,
    Direction,
    Jack,
    Panel,
    Pot,
    RotarySwitch,
    Section,
    ToggleSwitch,
)


def test_component_cannot_be_instantiated():
    with pytest.raises(TypeError):
        Component()


def test_panel():
    Panel(
        name="VCF",
        width_hp=8,
        sections=[
            Section(
                label="Input",
                components=[
                    Jack(label="Audio In"),
                    Jack(label="CV"),
                ],
            ),
            Section(
                label="Controls",
                direction=Direction.HORIZONTAL,
                components=[
                    Pot(label="Cutoff", value="100K"),
                    Pot(label="Resonance", value="100K"),
                    ToggleSwitch(label="Mode"),
                    RotarySwitch(label="Waveform", poles=1, throws=4),
                ],
            ),
            Section(
                label="Output",
                components=[
                    Jack(label="Audio Out"),
                    LED(label="Clip"),
                ],
            ),
            Section(
                label="Nested",
                direction=Direction.HORIZONTAL,
                components=[
                    Section(
                        label="Left",
                        direction=Direction.VERTICAL,
                        components=[Jack(label="In 1"), Jack(label="In 2")],
                    ),
                    Section(
                        label="Right",
                        direction=Direction.VERTICAL,
                        components=[Jack(label="Out 1"), Jack(label="Out 2")],
                    ),
                ],
            ),
        ],
    )
