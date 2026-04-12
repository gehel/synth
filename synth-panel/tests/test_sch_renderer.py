from __future__ import annotations

from pathlib import Path

import pytest

from synth_panel import LED, Jack, Panel, Pot, RotarySwitch, Section, ToggleSwitch, SchematicRenderer


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


def _sch_path(tmp_path, panel):
    return tmp_path / panel.name / f"{panel.name}.kicad_sch"


# ── File creation ─────────────────────────────────────────────────────────────

def test_render_schematic_creates_sch_file(tmp_path):
    panel = _panel()
    SchematicRenderer(tmp_path).render(panel)
    assert _sch_path(tmp_path, panel).exists()


def test_render_schematic_creates_project_files(tmp_path):
    panel = _panel()
    SchematicRenderer(tmp_path).render(panel)
    base = tmp_path / panel.name / panel.name
    assert base.with_suffix(".kicad_pro").exists()
    assert base.with_suffix(".kicad_pcb").exists()
    assert base.with_suffix(".kicad_prl").exists()


def test_render_schematic_creates_parent_dirs(tmp_path):
    panel = _panel()
    output_dir = tmp_path / "deep" / "nested"
    SchematicRenderer(output_dir).render(panel)
    assert _sch_path(tmp_path / "deep" / "nested", panel).exists()


# ── File content — symbols present ───────────────────────────────────────────

def test_render_schematic_contains_jack_symbol(tmp_path):
    panel = _panel()
    SchematicRenderer(tmp_path).render(panel)
    content = _sch_path(tmp_path, panel).read_text()
    assert "AudioJack2" in content


def test_render_schematic_contains_pot_symbol(tmp_path):
    panel = _panel()
    SchematicRenderer(tmp_path).render(panel)
    content = _sch_path(tmp_path, panel).read_text()
    assert "R_Potentiometer_MountingPin" in content


def test_render_schematic_contains_labels(tmp_path):
    panel = _panel()
    SchematicRenderer(tmp_path).render(panel)
    content = _sch_path(tmp_path, panel).read_text()
    assert "IN" in content
    assert "CUTOFF" in content
    assert "OUT" in content


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
    SchematicRenderer(tmp_path).render(panel)
    content = (tmp_path / "all_types" / "all_types.kicad_sch").read_text()
    assert "AudioJack2" in content
    assert "R_Potentiometer_MountingPin" in content
    assert "SW_SPDT" in content
    assert "SW_Rotary_1x12" in content
    assert "Device:LED" in content


# ── Reference designators ─────────────────────────────────────────────────────

def test_render_schematic_reference_designators(tmp_path):
    panel = Panel(
        name="refs",
        width_hp=8,
        sections=[Section(components=[Jack(label="A"), Jack(label="B"), Pot(label="C")])],
    )
    SchematicRenderer(tmp_path).render(panel)
    content = (tmp_path / "refs" / "refs.kicad_sch").read_text()
    assert '"J1"' in content
    assert '"J2"' in content
    assert '"RV1"' in content


# ── KiCad 9 format ───────────────────────────────────────────────────────────

def test_render_schematic_kicad9_version(tmp_path):
    panel = _panel()
    SchematicRenderer(tmp_path).render(panel)
    content = _sch_path(tmp_path, panel).read_text()
    assert "(version 20250114)" in content


def test_render_schematic_is_valid_kicad_sch(tmp_path):
    panel = _panel()
    SchematicRenderer(tmp_path).render(panel)
    content = _sch_path(tmp_path, panel).read_text()
    assert content.strip().startswith("(kicad_sch")
    assert content.strip().endswith(")")

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
    SchematicRenderer(output_dir).render(panel)
    assert (output_dir / panel.name / f"{panel.name}.kicad_sch").exists()