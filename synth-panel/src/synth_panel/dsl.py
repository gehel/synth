from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import kicad_sch_api as ksa


class LibraryEntry:
    def __init__(self, library: str, id: str) -> None:
        self._id = id
        self._library = library

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
class Element(ABC):
    n: Optional[int] = field(default=None, kw_only=True)
    label: Optional[str] = field(default=None, kw_only=True)
    _parent: Optional[Element] = field(default=None, init=False, repr=False, compare=False)

    @property
    def stable_id(self) -> str:
        return f"{type(self).__name__}_{self.n}"

    @property
    def root(self) -> Optional[Panel]:
        node = self
        while node is not None and not isinstance(node, Panel):
            node = node._parent
        return node if isinstance(node, Panel) else None


@dataclass
class Section(Element):
    direction: Direction = Direction.VERTICAL
    components: list[Element] = field(default_factory=list)

    def __post_init__(self) -> None:
        for child in self.components:
            child._parent = self


@dataclass
class Component(Element):
    value: Optional[str] = None

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
        kicad_comp = sch.components.add(
            str(self.symbol()),
            reference,
            value=(self.label or type(self).__name__),
            footprint=str(self.footprint()),
            position=(grid_x, grid_y),
        )
        kicad_comp.add_property("synth_panel_id", self.stable_id, hidden=False)


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


def find_next_id(used_ids: set[int]) -> int:
    n = 1
    while n in used_ids:
        n += 1
    return n


@dataclass
class Panel(Element):
    name: str
    width_hp: int
    sections: list[Section] = field(default_factory=list)

    def __post_init__(self) -> None:
        holes = Section(components=[MountingHole() for _ in range(4)])
        self.sections = [*self.sections, holes]
        for section in self.sections:
            section._parent = self
        self._assign_ids()

    @property
    def stable_id(self) -> str:
        return f"Panel_{self.name}"

    @property
    def mounting_holes(self) -> list[MountingHole]:
        return [
            c
            for section in self.sections
            for c in section.components
            if isinstance(c, MountingHole)
        ]

    def _assign_ids(self) -> None:
        comp_ids: dict[str, set[int]] = {}
        sec_ids: set[int] = set()
        for section in self.sections:
            self._assign_section_ids(section, comp_ids, sec_ids)

    def _assign_section_ids(
        self,
        section: Section,
        comp_ids: dict[str, set[int]],
        sec_ids: set[int],
    ) -> None:
        if section.n is None:
            section.n = find_next_id(sec_ids)
        elif section.n in sec_ids:
            raise ValueError(
                f"Section with n={section.n} already exists; "
                f"n must be unique across all sections"
            )
        assert section.n is not None
        sec_ids.add(section.n)
        for child in section.components:
            if isinstance(child, Section):
                self._assign_section_ids(child, comp_ids, sec_ids)
            elif isinstance(child, Component):
                self._assign_component_id(child, comp_ids)

    def _assign_component_id(
        self,
        comp: Component,
        comp_ids: dict[str, set[int]],
    ) -> None:
        cls_name = type(comp).__name__
        used = comp_ids.setdefault(cls_name, set())
        if comp.n is None:
            comp.n = find_next_id(used)
        elif comp.n in used:
            raise ValueError(
                f"{cls_name} with n={comp.n} already exists; "
                f"n must be unique per class"
            )
        assert comp.n is not None
        used.add(comp.n)