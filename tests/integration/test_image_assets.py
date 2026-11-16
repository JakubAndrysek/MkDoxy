"""Image URLs must resolve to the original bytes in the built documentation."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

import pytest

from .project import BuildOptions, ProjectBuilder

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


@pytest.mark.parametrize("api_path", ["xml", "xml/api"])
def test_api_path_can_overlap_doxygen_xml(build_project: ProjectBuilder, api_path: str) -> None:
    project = build_project("image_assets", options=BuildOptions(api_path=api_path))
    assert (project.root / "site" / api_path / "classImageExample/index.html").is_file()
    for image in (project.root / "images").iterdir():
        assert (project.root / "site" / api_path / image.name).read_bytes() == image.read_bytes()
