from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from synth_panel.dsl import Component

T = TypeVar("T")


class ComponentFactory(ABC, Generic[T]):
    """Abstract factory that produces output-specific representations of a DSL component.

    Subclasses specialise *T* for a particular output format (schematic, PCB, …).
    """

    @abstractmethod
    def create(self, component: Component) -> T: ...