"""Image URLs must resolve to the original bytes in the built documentation."""

import os
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

import pytest

from .project import BuildOptions, BuiltProject, ProjectBuilder
from .runner import run_build

pytestmark = pytest.mark.integration


class _ImageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sources: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "img":
            source = dict(attrs).get("src")
            if source:
                self.sources.append(source)


@pytest.mark.parametrize("api_path", [None, "reference/cpp"])
@pytest.mark.parametrize("save_api", [None, "cache/doxygen"])
@pytest.mark.parametrize("directory_urls", [True, False])
def test_doxygen_image_reaches_html(
    build_project: ProjectBuilder, api_path: str | None, save_api: str | None, directory_urls: bool
) -> None:
    project = build_project(
        "image_assets",
        options=BuildOptions(api_path=api_path, save_api=save_api, use_directory_urls=directory_urls),
    )
    assert project.api_path == (api_path or "api")
    assert project.save_api == (save_api or "")
    expected_names = {
        "pipeline.svg",
        "stages.png",
        "signal.jpg",
        "bars.jpeg",
        "progress.gif",
        "pixels.bmp",
        "coverage.webp",
    }
    images = [node for xml in project.xml_dir.glob("*.xml") for node in ElementTree.parse(xml).findall(".//image")]
    assert {node.get("name") for node in images} == expected_names
    markdown = project.markdown("classImageExample.md")
    page = Path(project.api_path) / ("classImageExample/index.html" if directory_urls else "classImageExample.html")
    parser = _ImageParser()
    parser.feed(project.html(page.as_posix()))
    for name in sorted(expected_names):
        assert f"![Image]({name})" in markdown
        sources = [source for source in parser.sources if Path(urlsplit(source).path).name == name]
        assert len(sources) == 1, (name, parser.sources)
        url = urlsplit(sources[0])
        assert not url.scheme and not url.netloc and not url.query and not url.fragment
        target = (project.root / "site" / page.parent / unquote(url.path)).resolve()
        expected = (project.root / "site" / project.api_path / name).resolve()
        assert target == expected
        original = (project.root / "images" / name).read_bytes()
        assert target.read_bytes() == original
        assert (project.generated_dir / project.api_path / name).read_bytes() == original


@pytest.mark.parametrize("identical", [True, False])
def test_existing_documentation_image_collision(build_project: ProjectBuilder, identical: bool) -> None:
    def prepare(root: Path) -> None:
        duplicate = root / "docs/api/pipeline.svg"
        duplicate.parent.mkdir(parents=True)
        original = (root / "images/pipeline.svg").read_bytes()
        duplicate.write_bytes(
            original if identical else b'<svg xmlns="http://www.w3.org/2000/svg"><text>stale</text></svg>'
        )

    if identical:
        project = build_project("image_assets", prepare=prepare)
        assert (project.root / "site/api/pipeline.svg").read_bytes() == (
            project.root / "images/pipeline.svg"
        ).read_bytes()
    else:
        with pytest.raises(AssertionError, match="Doxygen image conflicts"):
            build_project("image_assets", prepare=prepare)


@pytest.mark.parametrize("url", ["/media/site-image.svg", "https://example.com/remote.svg"])
def test_markdown_image_urls_remain_urls(build_project: ProjectBuilder, url: str) -> None:
    def prepare(root: Path) -> None:
        header = root / "src/image_example.h"
        header.write_text(
            header.read_text(encoding="utf-8").replace(
                " * SVG: resolution-independent pipeline diagram.",
                f" * ![External image]({url})\n *\n * SVG: resolution-independent pipeline diagram.",
            ),
            encoding="utf-8",
        )

    project = build_project("image_assets", prepare=prepare)
    assert f"![Image]({url})" in project.markdown("classImageExample.md")
    parser = _ImageParser()
    parser.feed(project.html("api/classImageExample/index.html"))
    assert url in parser.sources
    assert not (project.root / "site/api" / Path(urlsplit(url).path).name).exists()
    assert (project.root / "site/api/pipeline.svg").read_bytes() == (project.root / "images/pipeline.svg").read_bytes()


@pytest.mark.parametrize("api_path", ["xml", "xml/api"])
def test_api_path_can_overlap_doxygen_xml(build_project: ProjectBuilder, api_path: str) -> None:
    project = build_project("image_assets", options=BuildOptions(api_path=api_path))
    assert (project.root / "site" / api_path / "classImageExample/index.html").is_file()
    for image in (project.root / "images").iterdir():
        assert (project.root / "site" / api_path / image.name).read_bytes() == image.read_bytes()


def test_saved_output_cannot_overwrite_documentation_sources(build_project: ProjectBuilder) -> None:
    originals: list[Path] = []

    def prepare(root: Path) -> None:
        original = root / "docs/api/api/pipeline.svg"
        original.parent.mkdir(parents=True)
        original.write_text("original documentation asset", encoding="utf-8")
        originals.append(original)

    with pytest.raises(AssertionError, match="must not overlap docs_dir"):
        build_project("image_assets", options=BuildOptions(save_api="docs"), prepare=prepare)
    assert originals[0].read_text(encoding="utf-8") == "original documentation asset"


def rebuild_project(project: BuiltProject) -> None:
    doxygen = shutil.which("doxygen")
    assert doxygen is not None
    env = {
        "PATH": os.pathsep.join((str(Path(sys.executable).parent), str(Path(doxygen).parent), os.defpath)),
        "HOME": str(project.root / "home"),
        "USERPROFILE": str(project.root / "home"),
        "PYTHONPATH": str(Path(__file__).resolve().parents[2]),
        "PYTHONUTF8": "1",
    }
    if "SYSTEMROOT" in os.environ:
        env["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
    result = run_build([sys.executable, "-m", "mkdocs", "build", "--clean", "--strict"], project.root, env)
    assert result.returncode == 0, result.stdout


def test_persistent_images_update_and_removed_references_disappear(build_project: ProjectBuilder) -> None:
    def prepare(root: Path) -> None:
        xml = root / "cache/doxygen/api/xml"
        xml.mkdir(parents=True)
        (xml / "unused.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        (xml / "obsolete.xml").write_text(
            '<doxygen><compounddef><image type="html" name="unused.svg"/></compounddef></doxygen>', encoding="utf-8"
        )

    project = build_project("image_assets", options=BuildOptions(save_api="cache/doxygen"), prepare=prepare)
    assert not (project.root / "site/api/unused.svg").exists()
    image = project.root / "images/pipeline.svg"
    image.write_bytes(image.read_bytes() + b"\n<!-- updated without changing C++ sources -->\n")
    rebuild_project(project)
    assert (project.root / "site/api/pipeline.svg").read_bytes() == image.read_bytes()

    header = project.root / "src/image_example.h"
    header.write_text(
        "\n".join(line for line in header.read_text(encoding="utf-8").splitlines() if "@image html" not in line) + "\n",
        encoding="utf-8",
    )
    rebuild_project(project)
    for asset in (project.root / "images").iterdir():
        assert not (project.root / "site/api" / asset.name).exists()
    assert not (project.root / "site/api/unused.svg").exists()
