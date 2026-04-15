from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

import kicad_sch_api as ksa

from synth_panel.dsl import LED, Component, Jack, Pot, RotarySwitch, ToggleSwitch

# ── Product hierarchy ──────────────────────────────────────────────────────────

class LibraryEntry:
    def __init__(self, library: str, id: str) -> None:
        self._library = library
        self._id = id

    def library(self) -> str:
        return self._library

    def id(self) -> str:
        return self._id

    def __str__(self) -> str:
        return f"{self._library}:{self._id}"


class Symbol(LibraryEntry):
    pass


class Footprint(LibraryEntry):
    pass


UNKNOWN_FOOTPRINT = Footprint("Unknown", "Unknown")


class ComponentFactory(ABC):
    """Abstract factory that produces output-specific representations of a DSL component.

    Subclasses specialise *T* for a particular output format (schematic, PCB, …).
    """

    @abstractmethod
    def create(self, component: Component) -> SchematicComponent: ...


class SchematicComponent:
    """A DSL component that knows how to place itself in a KiCad schematic."""

    def __init__(self, symbol: Symbol, footprint: Footprint) -> None:
        self._symbol = symbol
        self._footprint = footprint

    def add_to_schematic(
        self,
        sch: ksa.Schematic,
        value: str,
        grid_x: int,
        grid_y: int,
    ) -> None:
        sch.components.add(
            str(self.symbol()),
            value=value,
            footprint=str(self.footprint()),
            position=(grid_x, grid_y),
        )

    def symbol(self) -> Symbol:
        return self._symbol

    def footprint(self) -> Footprint:
        return self._footprint


class JackSchematicComponent(SchematicComponent):
    def __init__(self):
        super().__init__(Symbol("Connector_Audio", "AudioJack2"), UNKNOWN_FOOTPRINT)


class PotSchematicComponent(SchematicComponent):
    def __init__(self) -> None:
        super().__init__(Symbol("Device", "R_Potentiometer_MountingPin"), UNKNOWN_FOOTPRINT)


class ToggleSwitchSchematicComponent(SchematicComponent):
    def __init__(self) -> None:
        super().__init__(Symbol("Switch", "SW_SPDT"), UNKNOWN_FOOTPRINT)


class LEDSchematicComponent(SchematicComponent):
    def __init__(self) -> None:
        super().__init__(Symbol("Device", "LED"), UNKNOWN_FOOTPRINT)


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
        super().__init__(Symbol("Switch", component_id), UNKNOWN_FOOTPRINT)
        self._component_id = component_id


# ── Factory ────────────────────────────────────────────────────────────────────

_Creators = dict[type[Component], Callable[[Component], SchematicComponent]]  # noqa: UP006


class SchematicComponentFactory(ComponentFactory):
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
