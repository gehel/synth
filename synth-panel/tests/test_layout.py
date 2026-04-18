import pytest

from synth_panel.dsl import LED, Direction, Jack, Panel, Pot, RotarySwitch, Section, ToggleSwitch
from synth_panel.layout import (
    COMPONENT_MARGIN,
    HP,
    PANEL_MARGIN,
    SECTION_MARGIN,
    SECTION_PADDING,
    PlacedComponent,
    lay_out,
)


def test_single_component_centered_horizontally():
    panel = Panel(
        name="Test",
        width_hp=4,
        sections=[
            Section(components=[Jack()]),
        ],
    )
    placed = lay_out(panel)

    assert len(placed) == 1
    assert placed[0].x == pytest.approx(panel.width_hp * HP / 2)


def test_single_component_vertical_position():
    panel = Panel(
        name="Test",
        width_hp=4,
        sections=[
            Section(components=[Jack()])  # Jack size = 12mm
        ],
    )
    placed = lay_out(panel)

    expected_y = PANEL_MARGIN + SECTION_PADDING + 12.0 / 2
    assert placed[0].y == pytest.approx(expected_y)


def test_two_components_in_vertical_section():
    panel = Panel(
        name="Test",
        width_hp=4,
        sections=[
            Section(components=[Jack(), Pot()])  # Jack=12mm, Pot=18mm
        ],
    )
    placed = lay_out(panel)

    assert len(placed) == 2
    jack_y = PANEL_MARGIN + SECTION_PADDING + 12.0 / 2
    pot_y = PANEL_MARGIN + SECTION_PADDING + 12.0 + COMPONENT_MARGIN + 18.0 / 2
    assert placed[0].y == pytest.approx(jack_y)
    assert placed[1].y == pytest.approx(pot_y)


def test_section_margin_between_sections():
    panel = Panel(
        name="Test",
        width_hp=4,
        sections=[
            Section(components=[Jack()]),  # height = 2*PADDING + 12
            Section(components=[Pot()]),  # starts after first section + SECTION_MARGIN
        ],
    )
    placed = lay_out(panel)

    section1_height = 2 * SECTION_PADDING + 12.0
    pot_y = PANEL_MARGIN + section1_height + SECTION_MARGIN + SECTION_PADDING + 18.0 / 2
    assert placed[1].y == pytest.approx(pot_y)


def test_horizontal_section_distributes_x():
    panel = Panel(
        name="Test",
        width_hp=8,
        sections=[Section(direction=Direction.HORIZONTAL, components=[Jack(), Jack()])],
    )
    placed = lay_out(panel)

    panel_width = 8 * HP
    assert len(placed) == 2
    assert placed[0].x == pytest.approx(panel_width / 4)
    assert placed[1].x == pytest.approx(3 * panel_width / 4)


def test_horizontal_section_centers_vertically():
    panel = Panel(
        name="Test",
        width_hp=8,
        sections=[Section(direction=Direction.HORIZONTAL, components=[Jack(), Jack()])],
    )
    placed = lay_out(panel)

    section_height = 2 * SECTION_PADDING + 12.0
    expected_y = PANEL_MARGIN + section_height / 2
    assert placed[0].y == pytest.approx(expected_y)
    assert placed[1].y == pytest.approx(expected_y)


def test_nested_sections():
    panel = Panel(
        name="Test",
        width_hp=8,
        sections=[
            Section(
                direction=Direction.HORIZONTAL,
                components=[
                    Section(direction=Direction.VERTICAL, components=[Jack(), Jack()]),
                    Section(direction=Direction.VERTICAL, components=[Pot()]),
                ],
            )
        ],
    )
    placed = lay_out(panel)

    assert len(placed) == 3


def test_lay_out_returns_placed_components():
    panel = Panel(
        name="Test",
        width_hp=4,
        sections=[Section(components=[Jack(label="CV"), Pot(label="Cutoff", value="100K")])],
    )
    placed = lay_out(panel)

    assert all(isinstance(p, PlacedComponent) for p in placed)
    assert placed[0].component.label == "CV"
    assert placed[1].component.label == "Cutoff"


# ── reference assignment ──────────────────────────────────────────────────────


def test_references_assigned():
    panel = Panel(
        name="Test",
        width_hp=10,
        sections=[
            Section(components=[Jack(), Pot(), Jack(), ToggleSwitch(), RotarySwitch(), LED()])
        ],
    )
    placed = lay_out(panel)

    refs = [pc.reference for pc in placed]
    assert refs == ["J1", "RV1", "J2", "SW1", "SW2", "D1"]


def test_references_unique_across_sections():
    panel = Panel(
        name="Test",
        width_hp=4,
        sections=[
            Section(components=[Jack()]),
            Section(components=[Jack()]),
        ],
    )
    placed = lay_out(panel)

    assert placed[0].reference == "J1"
    assert placed[1].reference == "J2"