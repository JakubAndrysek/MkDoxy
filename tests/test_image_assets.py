"""Focused checks for recursive copying independent of Doxygen's flattening."""

import os
from pathlib import Path

import pytest

from mkdoxy.plugin import MkDoxy


@pytest.mark.parametrize("suffix", [".png", ".JPG", ".jpeg", ".gif", ".bmp", ".svg", ".webp"])
def test_copy_image_assets_preserves_nested_paths(tmp_path: Path, suffix: str) -> None:
    xml = tmp_path / "xml"
    image = xml / "nested" / "diagrams" / f"example{suffix}"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"asset content for byte-for-byte copying")
    (xml / "index.xml").write_text("<doxygenindex/>", encoding="utf-8")
    destination = tmp_path / "api"

    copied = MkDoxy()._copy_image_assets(xml, destination)

    assert copied == [image.relative_to(xml)]
    assert (destination / copied[0]).read_bytes() == image.read_bytes()
    assert not (destination / "index.xml").exists()


def test_copy_image_assets_handles_missing_directory(tmp_path: Path) -> None:
    destination = tmp_path / "api"
    assert MkDoxy()._copy_image_assets(tmp_path / "missing", destination) == []
    assert not destination.exists()


def test_image_copy_failure_aborts_build(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from mkdocs.exceptions import PluginError

    xml = tmp_path / "xml"
    xml.mkdir()
    (xml / "image.svg").write_text("<svg/>", encoding="utf-8")

    def fail_copy(*args, **kwargs):
        raise PermissionError("asset is not writable")

    monkeypatch.setattr("mkdoxy.plugin.shutil.copy2", fail_copy)
    with pytest.raises(PluginError, match="image.svg"):
        MkDoxy()._copy_image_assets(xml, tmp_path / "api")


@pytest.mark.parametrize("output", ["xml", "xml/api"])
def test_image_copy_handles_overlapping_directories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, output: str
) -> None:
    import shutil

    xml = tmp_path / "xml"
    xml.mkdir()
    image = xml / "image.svg"
    image.write_text("<svg/>", encoding="utf-8")
    destination = tmp_path / output
    destination.mkdir(exist_ok=True)
    if destination != xml:
        (destination / "old.svg").write_text("old output", encoding="utf-8")
    original_copy = shutil.copy2
    copies = 0

    def bounded_copy(source, target):
        nonlocal copies
        copies += 1
        if copies > 3:
            pytest.fail("Image discovery is recursively copying its own output")
        return original_copy(source, target)

    monkeypatch.setattr("mkdoxy.plugin.shutil.copy2", bounded_copy)
    copied = MkDoxy()._copy_image_assets(xml, destination)
    assert copied == [Path("image.svg")]
    assert (destination / "image.svg").read_bytes() == image.read_bytes()
    assert not (destination / "api").exists()


@pytest.mark.skipif(os.name != "posix", reason="Requires POSIX symlinks")
def test_image_copy_rejects_source_symlink_escape(tmp_path: Path) -> None:
    from mkdocs.exceptions import PluginError

    xml = tmp_path / "xml"
    xml.mkdir()
    private = tmp_path / "private.txt"
    private.write_text("test-only private data", encoding="utf-8")
    (xml / "image.svg").symlink_to(private)
    with pytest.raises(PluginError, match="outside"):
        MkDoxy()._copy_image_assets(xml, tmp_path / "api")
    assert not (tmp_path / "api" / "image.svg").exists()


@pytest.mark.skipif(os.name != "posix", reason="Requires POSIX symlinks")
def test_image_copy_rejects_destination_symlink_escape(tmp_path: Path) -> None:
    from mkdocs.exceptions import PluginError

    xml = tmp_path / "xml"
    (xml / "nested").mkdir(parents=True)
    (xml / "nested" / "image.svg").write_text("<svg/>", encoding="utf-8")
    destination = tmp_path / "api"
    destination.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    private = outside / "image.svg"
    private.write_text("test-only private data", encoding="utf-8")
    (destination / "nested").symlink_to(outside, target_is_directory=True)
    with pytest.raises(PluginError, match="outside"):
        MkDoxy()._copy_image_assets(xml, destination)
    assert private.read_text(encoding="utf-8") == "test-only private data"
