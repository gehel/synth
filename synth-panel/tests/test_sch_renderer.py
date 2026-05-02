from __future__ import annotations

from pathlib import Path

import kicad_sch_api as ksa

from synth_panel import (
    LED,
    Jack,
    KicadProject,
    Panel,
    Pot,
    RotarySwitch,
    SchematicRenderer,
    Section,
    ToggleSwitch,
)


def _panel() -> Panel:
    return Panel(
        name="test_vcf",
        width_hp=8,
        sections=[
            Section(
                components=[
                    Jack(label="IN"),
                    Pot(label="CUTOFF"),
                    Jack(label="OUT"),
                ]
            )
        ],
    )


def _panel_modified() -> Panel:
    return Panel(
        name="test_vcf",
        width_hp=6,
        sections=[
            Section(
                components=[
                    Pot(label="CUTOFF_MODIFIED", n=1),
                    Jack(label="OUT_MODIFIED", n=2),
                    Jack(label="IN_MODIFIED", n=1),
                ]
            )
        ],
    )


def _renderer(base: Path, panel: Panel) -> SchematicRenderer:
    return SchematicRenderer(KicadProject(base / panel.name))


def _sch_path(tmp_path, panel):
    return tmp_path / panel.name / f"{panel.name}.kicad_sch"


# ── File creation ─────────────────────────────────────────────────────────────


def test_render_schematic_creates_sch_file(tmp_path):
    panel = _panel()
    _renderer(tmp_path, panel).render(panel)
    assert _sch_path(tmp_path, panel).exists()


def test_render_schematic_creates_project_files(tmp_path):
    panel = _panel()
    _renderer(tmp_path, panel).render(panel)
    base = tmp_path / panel.name / panel.name
    assert base.with_suffix(".kicad_pro").exists()
    assert base.with_suffix(".kicad_pcb").exists()
    assert base.with_suffix(".kicad_prl").exists()


def test_render_schematic_creates_parent_dirs(tmp_path):
    panel = _panel()
    output_dir = tmp_path / "deep" / "nested"
    _renderer(output_dir, panel).render(panel)
    assert _sch_path(tmp_path / "deep" / "nested", panel).exists()


# ── File content — symbols present ───────────────────────────────────────────


def test_render_schematic_contains_jack_symbol(tmp_path):
    panel = _panel()
    _renderer(tmp_path, panel).render(panel)
    content = _sch_path(tmp_path, panel).read_text()
    assert "AudioJack2" in content


def test_render_schematic_contains_pot_symbol(tmp_path):
    panel = _panel()
    _renderer(tmp_path, panel).render(panel)
    content = _sch_path(tmp_path, panel).read_text()
    assert "R_Potentiometer_MountingPin" in content


def test_render_schematic_contains_labels(tmp_path):
    panel = _panel()
    _renderer(tmp_path, panel).render(panel)
    content = _sch_path(tmp_path, panel).read_text()
    assert "IN" in content
    assert "CUTOFF" in content
    assert "OUT" in content


def test_render_schematic_contains_stable_ids(tmp_path):
    panel = _panel()
    _renderer(tmp_path, panel).render(panel)
    content = _sch_path(tmp_path, panel).read_text()
    assert "Jack_1" in content
    assert "Pot_1" in content
    assert "Jack_2" in content


def test_synth_panel_id_property_retrievable_after_add(tmp_path):
    panel = _panel()
    _renderer(tmp_path, panel).render(panel)

    ksa.use_grid_units(True)
    sch = ksa.load_schematic(str(_sch_path(tmp_path, panel)))

    props = [c.get_property("synth_panel_id") for c in sch.components.filter()]
    assert all(p is not None for p in props)
    assert all(p["name"] == "synth_panel_id" for p in props)

    retrieved_ids = {p["value"] for p in props}
    expected_ids = {
        comp.stable_id
        for section in panel.sections
        for comp in section.components
    }
    assert expected_ids <= retrieved_ids


def test_render_schematic_all_component_types(tmp_path):
    panel = Panel(
        name="all_types",
        width_hp=10,
        sections=[
            Section(
                components=[
                    Jack(label="J"),
                    Pot(label="P"),
                    ToggleSwitch(label="T"),
                    RotarySwitch(label="R"),
                    LED(label="L"),
                ]
            )
        ],
    )
    _renderer(tmp_path, panel).render(panel)
    content = (tmp_path / "all_types" / "all_types.kicad_sch").read_text()
    assert "AudioJack2" in content
    assert "R_Potentiometer_MountingPin" in content
    assert "SW_SPDT" in content
    assert "SW_Rotary_1x12" in content
    assert "Device:LED" in content


# ── KiCad 9 format ───────────────────────────────────────────────────────────


def test_render_schematic_kicad9_version(tmp_path):
    panel = _panel()
    _renderer(tmp_path, panel).render(panel)
    content = _sch_path(tmp_path, panel).read_text()
    assert "(version 20250114)" in content


def test_render_schematic_is_valid_kicad_sch(tmp_path):
    panel = _panel()
    _renderer(tmp_path, panel).render(panel)
    content = _sch_path(tmp_path, panel).read_text()
    assert content.strip().startswith("(kicad_sch")
    assert content.strip().endswith(")")


def test_components_can_be_updated(tmp_path):
    panel = _panel()
    panel_modified = _panel_modified()
    _renderer(tmp_path, panel).render(panel)
    content = _sch_path(tmp_path, panel).read_text()
    assert content.strip().startswith("(kicad_sch")

    _renderer(tmp_path, panel_modified).render(panel_modified)
    content = _sch_path(tmp_path, panel).read_text()
    assert content.strip().startswith("(kicad_sch")
    # Components updated, not duplicated: count instance lib_id lines only
    assert content.count('(lib_id "Connector_Audio:AudioJack2")') == 2
    assert content.count('(lib_id "Device:R_Potentiometer_MountingPin")') == 1
    # Values reflect the modified panel
    assert "CUTOFF_MODIFIED" in content
    assert "OUT_MODIFIED" in content
    assert "IN_MODIFIED" in content

# ── Manual inspection ─────────────────────────────────────────────────────────


def test_render_schematic_manual_inspection():
    """Write a representative panel to output/ for manual validation in KiCad.

    Files are kept after the test run:
      output/manual_inspection/manual_inspection.kicad_sch
    """
    output_dir = Path(__file__).parent.parent / "output"
    panel = Panel(
        name="manual_inspection",
        width_hp=10,
        sections=[
            Section(
                components=[
                    Jack(label="IN"),
                    Pot(label="CUTOFF"),
                    Pot(label="RESONANCE"),
                    ToggleSwitch(label="MODE"),
                    RotarySwitch(label="RANGE", poles=1, throws=12),
                    LED(label="CLIP"),
                    Jack(label="OUT"),
                ]
            )
        ],
    )
    _renderer(output_dir, panel).render(panel)
    assert (output_dir / panel.name / f"{panel.name}.kicad_sch").exists()