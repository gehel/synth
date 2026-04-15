import pytest

from synth_panel import ASCIIRenderer
from synth_panel.ascii_renderer import PANEL_ROWS
from synth_panel.dsl import Direction, Jack, Panel, Pot, Section


def test_render_ascii_returns_string():
    panel = Panel(name="Test", width_hp=4, sections=[Section(components=[Jack()])])
    assert isinstance(ASCIIRenderer().render(panel), str)


def test_render_ascii_row_count():
    panel = Panel(name="Test", width_hp=4, sections=[Section(components=[Jack()])])
    lines = ASCIIRenderer().render(panel).split("\n")
    assert len(lines) == PANEL_ROWS + 2


def test_render_ascii_all_rows_same_width():
    panel = Panel(name="Test", width_hp=8, sections=[Section(components=[Jack()])])
    lines = ASCIIRenderer().render(panel).split("\n")
    widths = {len(line) for line in lines}
    assert len(widths) == 1


def test_render_ascii_border_corners():
    panel = Panel(name="Test", width_hp=4, sections=[Section(components=[Jack()])])
    lines = ASCIIRenderer().render(panel).split("\n")
    assert lines[0][0] == "+"
    assert lines[0][-1] == "+"
    assert lines[-1][0] == "+"
    assert lines[-1][-1] == "+"


def test_render_ascii_jack_symbol_present():
    panel = Panel(name="Test", width_hp=4, sections=[Section(components=[Jack()])])
    assert "J" in ASCIIRenderer().render(panel)


def test_render_ascii_pot_symbol_present():
    panel = Panel(name="Test", width_hp=4, sections=[Section(components=[Pot()])])
    assert "P" in ASCIIRenderer().render(panel)


def test_render_ascii_label_present():
    panel = Panel(name="Test", width_hp=4, sections=[Section(components=[Jack(label="CV")])])
    assert "CV" in ASCIIRenderer().render(panel)


def test_render_ascii_multiple_labels():
    panel = Panel(
        name="Test",
        width_hp=4,
        sections=[Section(components=[Jack(label="IN"), Pot(label="Gain")])],
    )
    result = ASCIIRenderer().render(panel)
    assert "IN" in result
    assert "Gain" in result


def test_render_ascii_horizontal_section():
    panel = Panel(
        name="Test",
        width_hp=8,
        sections=[
            Section(direction=Direction.HORIZONTAL, components=[Jack(label="L"), Jack(label="R")])
        ],
    )
    result = ASCIIRenderer().render(panel)
    assert result.count("J") == 2


def test_render_ascii_visual(capsys):
    panel = Panel(
        name="Demo",
        width_hp=8,
        sections=[
            Section(
                components=[
                    Section(
                        direction=Direction.HORIZONTAL,
                        components=[
                            Pot(label="Coarse"),
                            Pot(label="Fine"),
                        ],
                    ),
                    Section(
                        direction=Direction.HORIZONTAL,
                        components=[
                            Pot(label="Pulse Width"),
                            Section(
                                direction=Direction.VERTICAL,
                                components=[
                                    Jack(label="Triangle"),
                                    Jack(label="Sine"),
                                ],
                            ),
                        ],
                    ),
                    Section(
                        direction=Direction.HORIZONTAL,
                        components=[
                            Jack(label="PWM-CV"),
                            Jack(label="Square"),
                            Jack(label="Sawtooth"),
                        ],
                    ),
                    Section(
                        direction=Direction.HORIZONTAL,
                        components=[
                            Jack(label="Frequency CV1"),
                            Jack(label="Frequency CV2"),
                            Jack(label="Ramp"),
                        ],
                    ),
                ]
            ),
        ],
    )
    print(ASCIIRenderer().render(panel))


@pytest.mark.parametrize("width_hp", [4, 8, 12, 16])
def test_render_ascii_various_widths(width_hp: int):
    panel = Panel(name="Test", width_hp=width_hp, sections=[Section(components=[Jack()])])
    lines = ASCIIRenderer().render(panel).split("\n")
    assert len(lines) == PANEL_ROWS + 2
    assert all(len(line) == len(lines[0]) for line in lines)
