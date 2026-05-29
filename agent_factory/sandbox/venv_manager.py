from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from agent_factory.config import SANDBOX_TIMEOUT_SECONDS


class VenvManager:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.path = self.project_path / ".venv"

    def create(self) -> None:
        subprocess.run(
            [sys.executable, "-m", "venv", str(self.path)],
            check=True,
            capture_output=True,
        )

    def install(self, libraries: list[str]) -> None:
        libraries = [l for l in (libraries or []) if str(l).strip()]
        if not libraries:
            return

        pip_bin = self._pip_bin()
        subprocess.run(
            [pip_bin, "install", *libraries],
            check=True,
            capture_output=True,
            timeout=SANDBOX_TIMEOUT_SECONDS,
        )

    def destroy(self) -> None:
        import shutil

        shutil.rmtree(self.path, ignore_errors=True)

    def _scripts_dir(self) -> Path:
        # Windows venvs use Scripts/, POSIX use bin/
        return self.path / ("Scripts" if os.name == "nt" else "bin")

    def _pip_bin(self) -> str:
        """Return the absolute path to the venv pip binary (public for use by TesterAgent)."""
        pip_name = "pip.exe" if os.name == "nt" else "pip"
        return str(self._scripts_dir() / pip_name)

    @property
    def python(self) -> str:
        py_name = "python.exe" if os.name == "nt" else "python"
        return str(self._scripts_dir() / py_name)

    @property
    def pytest(self) -> str:
        # Prefer direct pytest binary when available; fallback to python -m pytest.
        pytest_name = "pytest.exe" if os.name == "nt" else "pytest"
        candidate = self._scripts_dir() / pytest_name
        return str(candidate) if candidate.exists() else self.python

