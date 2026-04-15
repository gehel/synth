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


# ── symbol() returns the correct KiCad reference ─────────────────────────────


@pytest.mark.parametrize(
    "component, expected_symbol",
    [
        (Jack(), "Connector_Audio:AudioJack2"),
        (Pot(), "Device:R_Potentiometer_MountingPin"),
        (ToggleSwitch(), "Switch:SW_SPDT"),
        (LED(), "Device:LED"),
        (RotarySwitch(poles=1, throws=12), "Switch:SW_Rotary_1x12"),
        (RotarySwitch(poles=3, throws=4), "Switch:SW_Rotary_3x4"),
    ],
)
def test_symbol(component, expected_symbol):
    assert str(component.symbol()) == expected_symbol


def test_rotary_switch_unsupported_config_raises():
    with pytest.raises(ValueError, match="No KiCad symbol"):
        RotarySwitch(poles=2, throws=6).symbol()


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
