from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Direction(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass
class Component:
    label: Optional[str] = None
    value: Optional[str] = None

    def __post_init__(self) -> None:
        if type(self) is Component:
            raise TypeError("Component cannot be instantiated directly")


@dataclass
class Jack(Component):
    pass


@dataclass
class Pot(Component):
    pass


@dataclass
class ToggleSwitch(Component):
    pass


@dataclass
class RotarySwitch(Component):
    poles: int = 1
    throws: int = 12


@dataclass
class LED(Component):
    pass


@dataclass
class Section:
    label: Optional[str] = None
    direction: Direction = Direction.VERTICAL
    components: list[Component | Section] = field(default_factory=list)


@dataclass
class Panel:
    name: str
    width_hp: int
    sections: list[Section] = field(default_factory=list)