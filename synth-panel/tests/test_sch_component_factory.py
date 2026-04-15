from __future__ import annotations

import pytest

from synth_panel.dsl import LED, Jack, Pot, RotarySwitch, ToggleSwitch
from synth_panel.sch_component_factory import SchematicComponent, SchematicComponentFactory


@pytest.fixture
def factory() -> SchematicComponentFactory:
    return SchematicComponentFactory()


# ── create() returns a SchematicComponent ─────────────────────────────────────


@pytest.mark.parametrize(
    "component",
    [
        Jack(),
        Pot(),
        ToggleSwitch(),
        LED(),
        RotarySwitch(poles=1, throws=12),
        RotarySwitch(poles=3, throws=4),
    ],
)
def test_create_returns_schematic_component(factory, component):
    assert isinstance(factory.create(component), SchematicComponent)


# ── RotarySwitch error on unsupported configuration ───────────────────────────


def test_rotary_switch_unsupported_config_raises(factory):
    with pytest.raises(ValueError, match="No KiCad symbol"):
        factory.create(RotarySwitch(poles=2, throws=6))
