"""Focused checks for recursive copying independent of Doxygen's flattening."""

import os
from pathlib import Path, PurePath

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

    copied = MkDoxy()._copy_image_assets(xml, destination, image_names={image.relative_to(xml).as_posix()})

    assert copied == [image.relative_to(xml)]
    assert (destination / copied[0]).read_bytes() == image.read_bytes()
    assert not (destination / "index.xml").exists()


def test_copy_image_assets_handles_missing_directory(tmp_path: Path) -> None:
    destination = tmp_path / "api"
    assert MkDoxy()._copy_image_assets(tmp_path / "missing", destination, image_names=set()) == []
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
        MkDoxy()._copy_image_assets(xml, tmp_path / "api", image_names={"image.svg"})


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
    copied = MkDoxy()._copy_image_assets(xml, destination, image_names={"image.svg"})
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
        MkDoxy()._copy_image_assets(xml, tmp_path / "api", image_names={"image.svg"})
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
        MkDoxy()._copy_image_assets(xml, destination, image_names={"nested/image.svg"})
    assert private.read_text(encoding="utf-8") == "test-only private data"


def test_only_referenced_images_are_copied(tmp_path: Path) -> None:
    xml = tmp_path / "xml"
    xml.mkdir()
    (xml / "current.svg").write_text("<svg/>", encoding="utf-8")
    (xml / "removed.svg").write_text("<svg/>", encoding="utf-8")
    destination = tmp_path / "api"
    assert MkDoxy()._copy_image_assets(xml, destination, image_names={"current.svg"}) == [Path("current.svg")]
    assert not (destination / "removed.svg").exists()


def test_current_nested_image_is_not_excluded_with_overlapping_output(tmp_path: Path) -> None:
    xml = tmp_path / "xml"
    (xml / "api").mkdir(parents=True)
    (xml / "api/current.svg").write_text("<svg/>", encoding="utf-8")
    destination = xml / "api"
    copied = MkDoxy()._copy_image_assets(xml, destination, image_names={"api/current.svg"})
    assert copied == [Path("api/current.svg")]
    assert (destination / "api/current.svg").read_text(encoding="utf-8") == "<svg/>"
    assert not (destination / "api/api").exists()


def test_collision_check_precedes_copy(tmp_path: Path) -> None:
    from mkdocs.exceptions import PluginError

    xml = tmp_path / "xml"
    xml.mkdir()
    (xml / "image.svg").write_text("new input", encoding="utf-8")
    destination = tmp_path / "api"
    destination.mkdir()
    target = destination / "image.svg"
    target.write_text("original file", encoding="utf-8")

    def conflict(relative: PurePath, source: Path) -> None:
        raise PluginError("conflicting original documentation asset")

    with pytest.raises(PluginError, match="conflicting"):
        MkDoxy()._copy_image_assets(xml, destination, image_names={"image.svg"}, check_collision=conflict)
    assert target.read_text(encoding="utf-8") == "original file"


def test_remote_image_is_not_copied(tmp_path: Path) -> None:
    assert (
        MkDoxy()._copy_image_assets(tmp_path / "xml", tmp_path / "api", image_names={"https://example.com/image.svg"})
        == []
    )


def test_xml_image_path_cannot_escape_source(tmp_path: Path) -> None:
    from mkdocs.exceptions import PluginError

    with pytest.raises(PluginError, match="outside"):
        MkDoxy()._copy_image_assets(tmp_path / "xml", tmp_path / "api", image_names={"../private.svg"})


def test_absolute_image_url_is_not_read_or_copied(tmp_path: Path) -> None:
    private = tmp_path / "private.svg"
    private.write_bytes(b"host file must not be published")
    destination = tmp_path / "api"
    assert MkDoxy()._copy_image_assets(tmp_path / "xml", destination, image_names={str(private)}) == []
    assert private.read_bytes() == b"host file must not be published"
    assert not destination.exists()


def test_overlapping_output_cannot_replace_another_referenced_source(tmp_path: Path) -> None:
    from mkdocs.exceptions import PluginError

    xml = tmp_path / "xml"
    (xml / "api").mkdir(parents=True)
    root = xml / "image.svg"
    nested = xml / "api/image.svg"
    root.write_bytes(b"root image")
    nested.write_bytes(b"nested image")
    for _ in range(2):
        with pytest.raises(PluginError, match="overwrite another referenced XML image"):
            MkDoxy()._copy_image_assets(xml, xml / "api", image_names={"image.svg", "api/image.svg"})
        assert root.read_bytes() == b"root image"
        assert nested.read_bytes() == b"nested image"
        assert not (xml / "api/api").exists()
