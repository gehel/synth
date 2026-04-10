from __future__ import annotations

from dataclasses import dataclass

from synth_panel.dsl import (
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

HP: float = 5.08  # mm per HP
PANEL_HEIGHT: float = 128.5  # mm, Eurorack 3U
PANEL_MARGIN: float = 3.0  # mm, top and bottom (clear of mounting holes)
SECTION_MARGIN: float = 5.0  # mm between sections (space for delineation line)
SECTION_PADDING: float = 3.0  # mm inside a section, above first and below last child
COMPONENT_MARGIN: float = 2.0  # mm between components within a section

_COMPONENT_SIZE: dict[type[Component], float] = {  # noqa: UP006
    LED: 8.0,
    Jack: 12.0,
    ToggleSwitch: 12.0,
    Pot: 18.0,
    RotarySwitch: 22.0,
}


@dataclass
class PlacedComponent:
    component: Component
    x: float  # center x in mm from left edge of panel
    y: float  # center y in mm from top edge of panel


def lay_out(panel: Panel) -> list[PlacedComponent]:
    panel_width = panel.width_hp * HP
    x_center = panel_width / 2
    placed: list[PlacedComponent] = []

    y = PANEL_MARGIN
    for i, section in enumerate(panel.sections):
        h = _section_height(section)
        _place_section(section, x_center, y, panel_width, h, placed)
        y += h
        if i < len(panel.sections) - 1:
            y += SECTION_MARGIN

    return placed


def _section_height(section: Section) -> float:
    if not section.components:
        return 2 * SECTION_PADDING

    children = section.components
    if section.direction == Direction.VERTICAL:
        heights = [_child_height(c) for c in children]
        return 2 * SECTION_PADDING + sum(heights) + (len(heights) - 1) * COMPONENT_MARGIN
    else:  # HORIZONTAL
        heights = [_child_height(c) for c in children]
        return 2 * SECTION_PADDING + max(heights)


def _child_height(child: Component | Section) -> float:
    if isinstance(child, Section):
        return _section_height(child)
    return _COMPONENT_SIZE[type(child)]


def _place_section(
    section: Section,
    x_center: float,
    y_top: float,
    width: float,
    height: float,
    placed: list[PlacedComponent],
) -> None:
    if not section.components:
        return

    if section.direction == Direction.VERTICAL:
        y = y_top + SECTION_PADDING
        for child in section.components:
            if isinstance(child, Section):
                child_h = _section_height(child)
                _place_section(child, x_center, y, width, child_h, placed)
                y += child_h + COMPONENT_MARGIN
            else:
                size = _COMPONENT_SIZE[type(child)]
                placed.append(PlacedComponent(child, x_center, y + size / 2))
                y += size + COMPONENT_MARGIN
    else:  # HORIZONTAL
        n = len(section.components)
        child_width = width / n
        y_center = y_top + height / 2

        for i, child in enumerate(section.components):
            child_x_center = x_center - width / 2 + (i + 0.5) * child_width
            if isinstance(child, Section):
                child_h = _section_height(child)
                _place_section(
                    child, child_x_center, y_center - child_h / 2, child_width, child_h, placed
                )
            else:
                placed.append(PlacedComponent(child, child_x_center, y_center))