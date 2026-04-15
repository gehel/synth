from __future__ import annotations

import shutil
from pathlib import Path

_TEMPLATE_DIR = Path(__file__).parent / "template" / "blank"
_PROJECT_SUFFIXES = (".kicad_sch", ".kicad_pro", ".kicad_pcb", ".kicad_prl")


class KicadProject:
    """Represents a KiCad project.

    By convention, the project directory name matches the project name.
    """

    def __init__(self, project_dir: Path) -> None:
        self._project_dir = project_dir

    @property
    def name(self) -> str:
        return self._project_dir.name

    @property
    def project_dir(self) -> Path:
        return self._project_dir

    def init_project(self) -> None:
        """Create project files from the blank template if they don't exist yet."""
        self._project_dir.mkdir(parents=True, exist_ok=True)
        for suffix in _PROJECT_SUFFIXES:
            dest_file = self._project_dir / f"{self.name}{suffix}"
            if not dest_file.exists():
                shutil.copy(_TEMPLATE_DIR / f"blank{suffix}", dest_file)
