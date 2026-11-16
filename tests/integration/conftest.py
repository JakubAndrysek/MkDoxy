"""Build small, repository-owned projects with real MkDocs and Doxygen."""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from .project import BuiltProject
from .runner import run_build


@pytest.fixture(scope="module")
def build_project(tmp_path_factory: pytest.TempPathFactory) -> Callable[[str], BuiltProject]:
    """Return a builder; missing tools and failed builds must fail, not skip."""
    doxygen = shutil.which("doxygen")
    if doxygen is None:
        pytest.fail("Integration tests require Doxygen on PATH; see CONTRIBUTING.md")
    source_root = Path(__file__).resolve().parents[2]
    fixtures = Path(__file__).parent / "fixtures"

    def build(name: str) -> BuiltProject:
        root = tmp_path_factory.mktemp(name)
        shutil.copytree(fixtures / name, root, dirs_exist_ok=True)
        home = root / "home"
        home.mkdir()
        # No developer credentials or environment-specific MkDocs configuration.
        env = {
            "PATH": os.pathsep.join((str(Path(sys.executable).parent), str(Path(doxygen).parent), os.defpath)),
            "HOME": str(home),
            "USERPROFILE": str(home),
            "XDG_CACHE_HOME": str(home / ".cache"),
            "PYTHONPATH": str(source_root),
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUTF8": "1",
        }
        if "SYSTEMROOT" in os.environ:
            env["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
        # Verify the entry point cannot silently exercise an installed release.
        runner = (
            "import sys; from pathlib import Path; import mkdoxy; "
            "expected = Path(sys.argv.pop(1)); "
            "assert Path(mkdoxy.__file__).resolve().parent == expected, mkdoxy.__file__; "
            "from mkdocs.__main__ import cli; cli()"
        )
        command = [sys.executable, "-c", runner, str(source_root / "mkdoxy"), "build", "--clean", "--strict"]
        try:
            result = run_build(command, root, env)
        except subprocess.TimeoutExpired:
            output = (root / "build.log").read_text(encoding="utf-8", errors="replace")
            pytest.fail(f"MkDocs build timed out in {root}:\n{output}")
        output = result.stdout
        assert result.returncode == 0, f"MkDocs build failed in {root}:\n{output}"
        assert (root / "site" / "index.html").is_file(), output
        assert (root / "generated" / "api" / "xml" / "index.xml").is_file(), output
        return BuiltProject(root)

    return build
