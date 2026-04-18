import pytest

from synth_panel.dsl import Component, Section


@pytest.fixture(autouse=True)
def reset_id_registry():
    Component._used_ids.clear()
    Section._used_ids.clear()