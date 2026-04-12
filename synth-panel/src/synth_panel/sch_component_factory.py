from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

import kicad_sch_api as ksa

from synth_panel.component_factory import ComponentFactory
from synth_panel.dsl import LED, Component, Jack, Pot, RotarySwitch, ToggleSwitch

# ── Product hierarchy ──────────────────────────────────────────────────────────


class SchematicComponent(ABC):
    """A DSL component that knows how to place itself in a KiCad schematic."""

    def add_to_schematic(
        self,
        sch: ksa.Schematic,
        value: str,
        grid_x: int,
        grid_y: int,
    ) -> None:
        sch.components.add(
            self.library() + ":" + self.component_id(),
            value=value, position=(grid_x, grid_y),
        )

    @abstractmethod
    def library(self) -> str:
        ...

    @abstractmethod
    def component_id(self) -> str:
        ...


class JackSchematicComponent(SchematicComponent):

    def library(self) -> str:
        return "Connector_Audio"

    def component_id(self) -> str:
        return "AudioJack2"


class PotSchematicComponent(SchematicComponent):

    def library(self) -> str:
        return "Device"

    def component_id(self) -> str:
        return "R_Potentiometer_MountingPin"


class ToggleSwitchSchematicComponent(SchematicComponent):
    def library(self) -> str:
        return "Switch"

    def component_id(self) -> str:
        return "SW_SPDT"


class LEDSchematicComponent(SchematicComponent):
    def library(self) -> str:
        return "Device"

    def component_id(self) -> str:
        return "LED"


_ROTARY_COMPONENT_ID: dict[tuple[int, int], str] = {
    (1, 12): "SW_Rotary_1x12",
    (3, 4): "SW_Rotary_3x4",
}


class RotarySwitchSchematicComponent(SchematicComponent):
    def __init__(self, component: RotarySwitch) -> None:
        key = (component.poles, component.throws)
        component_id = _ROTARY_COMPONENT_ID.get(key)
        if component_id is None:
            raise ValueError(
                f"No KiCad symbol for RotarySwitch "
                f"poles={component.poles}, throws={component.throws}. "
                f"Supported: {list(_ROTARY_COMPONENT_ID.keys())}"
            )
        self._component_id = component_id

    def library(self) -> str:
        return "Switch"

    def component_id(self) -> str:
        return self._component_id


# ── Factory ────────────────────────────────────────────────────────────────────

_Creators = dict[type[Component], Callable[[Component], SchematicComponent]]  # noqa: UP006


class SchematicComponentFactory(ComponentFactory[SchematicComponent]):
    """Creates the appropriate :class:`SchematicComponent` for any DSL component."""

    _creators: _Creators = {
        Jack: lambda c: JackSchematicComponent(),
        Pot: lambda c: PotSchematicComponent(),
        ToggleSwitch: lambda c: ToggleSwitchSchematicComponent(),
        LED: lambda c: LEDSchematicComponent(),
        RotarySwitch: lambda c: RotarySwitchSchematicComponent(c),  # type: ignore[arg-type]
    }

    def create(self, component: Component) -> SchematicComponent:
        creator = self._creators.get(type(component))
        if creator is None:
            raise KeyError(f"No schematic mapping for component type {type(component).__name__!r}")
        return creator(component)