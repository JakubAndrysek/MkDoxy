"""Cache validity includes external images and only certifies successful output."""

from pathlib import Path

import pytest

from mkdoxy.doxyrun import DoxygenRun


def make_run(tmp_path: Path) -> tuple[DoxygenRun, Path, Path]:
    source = tmp_path / "src"
    source.mkdir()
    header = source / "example.h"
    header.write_text("/** Example. @image html picture.svg */\nclass Example {};\n", encoding="utf-8")
    images = tmp_path / "image assets"
    images.mkdir()
    image = images / "picture.svg"
    image.write_text('<svg xmlns="http://www.w3.org/2000/svg"><title>before</title></svg>', encoding="utf-8")
    output = tmp_path / "generated"
    output.mkdir()
    runner = DoxygenRun(
        "doxygen",
        str(source),
        str(output),
        {"IMAGE_PATH": f'"{images}"', "EXAMPLE_PATH": "", "EXTRACT_ALL": True, "QUIET": True},
    )
    return runner, header, image


def test_cache_tracks_external_image_changes(tmp_path: Path) -> None:
    runner, _, image = make_run(tmp_path)
    assert runner.checkAndRun()
    assert not runner.hasChanged()
    image.write_text('<svg xmlns="http://www.w3.org/2000/svg"><title>after</title></svg>', encoding="utf-8")
    assert runner.hasChanged()
    assert runner.checkAndRun()
    assert (Path(runner.getOutputFolder()) / image.name).read_bytes() == image.read_bytes()
    assert not runner.checkAndRun()


def test_failed_run_is_retried_with_existing_xml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runner, header, _ = make_run(tmp_path)
    assert runner.checkAndRun()
    header.write_text("/** Updated. */\nclass Example { public: void changed(); };\n", encoding="utf-8")
    real_run = runner.run
    index = Path(runner.getOutputFolder()) / "index.xml"
    previous_index = index.read_bytes()

    def fail() -> None:
        # A failed generator may still leave a complete-looking stale index.
        index.write_bytes(previous_index)
        raise RuntimeError("simulated Doxygen failure")

    monkeypatch.setattr(runner, "run", fail)
    with pytest.raises(RuntimeError, match="simulated"):
        runner.checkAndRun()
    assert not Path(runner.hashFilePath).exists()
    assert index.is_file()
    monkeypatch.setattr(runner, "run", real_run)
    assert runner.checkAndRun()
    assert "changed" in (Path(runner.getOutputFolder()) / "classExample.xml").read_text(encoding="utf-8")
    assert not runner.checkAndRun()


def test_missing_index_invalidates_cache(tmp_path: Path) -> None:
    runner, _, _ = make_run(tmp_path)
    assert runner.checkAndRun()
    (Path(runner.getOutputFolder()) / "index.xml").unlink()
    assert runner.hasChanged()
    assert runner.checkAndRun()


def test_configuration_changes_invalidate_cache(tmp_path: Path) -> None:
    runner, _, _ = make_run(tmp_path)
    assert runner.checkAndRun()
    runner.doxyCfg["PROJECT_NAME"] = "Updated project"
    assert runner.hasChanged()
    assert runner.checkAndRun()


def test_hash_check_has_no_cache_write_side_effect(tmp_path: Path) -> None:
    runner, _, _ = make_run(tmp_path)
    assert runner.hasChanged()
    assert not Path(runner.hashFilePath).exists()
    assert runner.hasChanged()
