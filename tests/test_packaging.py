"""Exercise the source distribution, not just an editable checkout."""

import configparser
import email
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

from packaging.specifiers import SpecifierSet
from packaging.requirements import Requirement


def test_wheel_builds_from_sdist(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    source = tmp_path / "source"
    source.mkdir()
    for name in ("pyproject.toml", "README.md", "LICENSE", "requirements.txt", "devdeps.txt"):
        shutil.copy2(root / name, source / name)
    shutil.copytree(root / "mkdoxy", source / "mkdoxy", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    # A real importable decoy catches accidentally broad package discovery.
    (source / "tests").mkdir()
    (source / "tests" / "__init__.py").write_text("", encoding="utf-8")

    # The default command builds an sdist, then builds the wheel FROM it.
    # Use the build backend already installed by .[dev] or uv.
    # Find its executable even when pytest uses an unactivated venv's Python.
    build_env = dict(os.environ)
    build_env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + build_env.get("PATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "build", "--no-isolation"],
        cwd=source,
        env=build_env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    sdists = list((source / "dist").glob("*.tar.gz"))
    assert len(sdists) == 1
    with tarfile.open(sdists[0]) as sdist:
        source_names = {name.partition("/")[2] for name in sdist.getnames()}
        assert {"requirements.txt", "devdeps.txt", "tests/__init__.py"} <= source_names
    wheels = list((source / "dist").glob("*.whl"))
    assert len(wheels) == 1

    with zipfile.ZipFile(wheels[0]) as wheel:
        names = wheel.namelist()
        metadata_path = next(name for name in names if name.endswith(".dist-info/METADATA"))
        metadata = email.message_from_bytes(wheel.read(metadata_path))
        assert metadata["Name"] == "mkdoxy"
        requirements = [Requirement(value) for value in metadata.get_all("Requires-Dist", [])]
        assert any(value.name == "mkdocs" and value.marker is None for value in requirements)
        supported = SpecifierSet(metadata["Requires-Python"])
        assert "3.9" not in supported
        assert all(f"3.{minor}" in supported for minor in range(10, 16))
        expected_templates = {f"mkdoxy/templates/{p.name}" for p in (root / "mkdoxy/templates").glob("*.jinja2")}
        assert expected_templates
        assert expected_templates <= set(names)
        assert not any(name.startswith(("tests/", "tests-old/", "demo-projects/")) for name in names)
        entry_points = next(name for name in names if name.endswith(".dist-info/entry_points.txt"))
        entry_config = configparser.ConfigParser()
        entry_config.read_string(wheel.read(entry_points).decode())
        assert entry_config["mkdocs.plugins"]["mkdoxy"] == "mkdoxy.plugin:MkDoxy"
