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
from synth_panel.dsl import Element


def test_component_cannot_be_instantiated():
    with pytest.raises(TypeError):
        Component()


# ── reference_prefix() ───────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "component, expected_prefix",
    [
        (Jack(), "J"),
        (Pot(), "RV"),
        (ToggleSwitch(), "SW"),
        (RotarySwitch(), "SW"),
        (LED(), "D"),
    ],
)
def test_reference_prefix(component, expected_prefix):
    assert component.reference_prefix() == expected_prefix


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


# ── stable_id ────────────────────────────────────────────────────────────────


def test_stable_id_auto_assigned():
    panel = Panel(name="t", width_hp=4, sections=[Section(components=[Jack(), Jack()])])
    j1, j2 = panel.sections[0].components
    assert j1.stable_id == "Jack_1"
    assert j2.stable_id == "Jack_2"


def test_stable_id_explicit_n():
    assert Jack(n=42).stable_id == "Jack_42"


def test_stable_id_per_class_counter():
    panel = Panel(name="t", width_hp=4, sections=[Section(components=[Jack(), Pot()])])
    jack, pot = panel.sections[0].components
    assert jack.stable_id == "Jack_1"
    assert pot.stable_id == "Pot_1"


def test_stable_id_section():
    panel = Panel(name="t", width_hp=4, sections=[Section()])
    assert panel.sections[0].stable_id == "Section_1"


def test_duplicate_n_raises():
    with pytest.raises(ValueError, match="already exists"):
        Panel(name="t", width_hp=4, sections=[Section(components=[Jack(n=1), Jack(n=1)])])


def test_duplicate_n_different_classes_allowed():
    Panel(name="t", width_hp=4, sections=[Section(components=[Jack(n=1), Pot(n=1)])])


def test_duplicate_section_n_raises():
    with pytest.raises(ValueError, match="already exists"):
        Panel(name="t", width_hp=4, sections=[Section(n=1), Section(n=1)])


# ── parent references ─────────────────────────────────────────────────────────


def test_parent_set_on_section_creation():
    jack = Jack()
    section = Section(components=[jack])
    assert jack._parent is section


def test_parent_set_on_panel_creation():
    section = Section()
    panel = Panel(name="t", width_hp=4, sections=[section])
    assert section._parent is panel


def test_root_traversal():
    jack = Jack()
    section = Section(components=[jack])
    panel = Panel(name="t", width_hp=4, sections=[section])
    assert jack.root is panel


def test_root_of_panel_is_self():
    panel = Panel(name="t", width_hp=4)
    assert panel.root is panel


def test_element_hierarchy():
    assert isinstance(Jack(), Element)
    assert isinstance(Section(), Element)
    assert isinstance(Panel(name="t", width_hp=4), Element)