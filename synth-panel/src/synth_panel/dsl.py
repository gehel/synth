from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, Optional

import kicad_sch_api as ksa


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


class Direction(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass
class Component(ABC):
    _used_ids: ClassVar[dict[type, set[int]]] = {}

    n: Optional[int] = None
    label: Optional[str] = None
    value: Optional[str] = None

    def __post_init__(self) -> None:
        cls = type(self)
        used = Component._used_ids.setdefault(cls, set())
        if self.n is None:
            self.n = find_next_id(used)
        elif self.n in used:
            raise ValueError(
                f"{cls.__name__} with n={self.n} already exists; "
                f"n must be unique per class"
            )
        used.add(self.n)

    @property
    def stable_id(self) -> str:
        return f"{type(self).__name__}_{self.n}"

    @abstractmethod
    def symbol(self) -> Symbol: ...

    @abstractmethod
    def footprint(self) -> Footprint: ...

    @abstractmethod
    def reference_prefix(self) -> str: ...

    def add_to_schematic(
        self,
        sch: ksa.Schematic,
        reference: str,
        grid_x: int,
        grid_y: int,
    ) -> None:
        sch.components.add(
            str(self.symbol()),
            reference,
            value=(self.label or type(self).__name__),
            footprint=str(self.footprint()),
            position=(grid_x, grid_y),
        )


@dataclass
class Jack(Component):
    def symbol(self) -> Symbol:
        return Symbol("Connector_Audio", "AudioJack2")

    def footprint(self) -> Footprint:
        return Footprint("Library", "Jack_3.5mm_QingPu_WQP-PJ398SM_Vertical_CircularHoles-panel")

    def reference_prefix(self) -> str:
        return "J"


@dataclass
class Pot(Component):
    def symbol(self) -> Symbol:
        return Symbol("Device", "R_Potentiometer_MountingPin")

    def footprint(self) -> Footprint:
        return Footprint("Library", "Potentiometer_Bourns_PTV09A-1_Single_Vertical-panel")

    def reference_prefix(self) -> str:
        return "RV"


@dataclass
class ToggleSwitch(Component):
    def symbol(self) -> Symbol:
        return Symbol("Switch", "SW_SPDT")

    def footprint(self) -> Footprint:
        return UNKNOWN_FOOTPRINT

    def reference_prefix(self) -> str:
        return "SW"


_ROTARY_COMPONENT_ID: dict[tuple[int, int], str] = {
    (1, 12): "SW_Rotary_1x12",
    (3, 4): "SW_Rotary_3x4",
}


@dataclass
class RotarySwitch(Component):
    poles: int = 1
    throws: int = 12

    def symbol(self) -> Symbol:
        key = (self.poles, self.throws)
        component_id = _ROTARY_COMPONENT_ID.get(key)
        if component_id is None:
            raise ValueError(
                f"No KiCad symbol for RotarySwitch "
                f"poles={self.poles}, throws={self.throws}. "
                f"Supported: {list(_ROTARY_COMPONENT_ID.keys())}"
            )
        return Symbol("Switch", component_id)

    def footprint(self) -> Footprint:
        return UNKNOWN_FOOTPRINT

    def reference_prefix(self) -> str:
        return "SW"


@dataclass
class LED(Component):
    def symbol(self) -> Symbol:
        return Symbol("Device", "LED")

    def footprint(self) -> Footprint:
        return UNKNOWN_FOOTPRINT

    def reference_prefix(self) -> str:
        return "D"


@dataclass
class MountingHole(Component):
    def symbol(self) -> Symbol:
        return Symbol("Mechanical", "MountingHole")

    def footprint(self) -> Footprint:
        return Footprint("MountingHole", "MountingHole_3.2mm_M3")

    def reference_prefix(self) -> str:
        return "H"


@dataclass
class Section:
    _used_ids: ClassVar[set[int]] = set()

    n: Optional[int] = None
    label: Optional[str] = None
    direction: Direction = Direction.VERTICAL
    components: list[Component | Section] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.n is None:
            self.n = find_next_id(Section._used_ids)
        elif self.n in Section._used_ids:
            raise ValueError(
                f"Section with n={self.n} already exists; "
                f"n must be unique across all sections"
            )
        Section._used_ids.add(self.n)

    @property
    def stable_id(self) -> str:
        return f"Section_{self.n}"

def find_next_id(used_ids):
    n = 1
    while n in used_ids:
        n += 1
    return n

@dataclass
class Panel:
    name: str
    width_hp: int
    sections: list[Section] = field(default_factory=list)