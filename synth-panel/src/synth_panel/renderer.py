from __future__ import annotations

from abc import ABC, abstractmethod

from synth_panel.dsl import Panel


class Renderer(ABC):
    """Base class for all panel renderers."""

    @abstractmethod
    def render(self, panel: Panel) -> None: ...