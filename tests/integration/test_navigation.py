"""The generated API summary must contain its descendants and working links."""

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

import pytest
import yaml

from .project import BuildOptions, ProjectBuilder

pytestmark = pytest.mark.integration


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[tuple[str, int]] = []
        self.depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("ul", "ol"):
            self.depth += 1
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append((href, self.depth))

    def handle_endtag(self, tag: str) -> None:
        if tag in ("ul", "ol"):
            self.depth -= 1


@pytest.mark.parametrize("source_listing", [True, False])
@pytest.mark.parametrize("directory_urls", [True, False])
def test_summary_contains_descendants_and_valid_targets(
    build_project: ProjectBuilder, source_listing: bool, directory_urls: bool
) -> None:
    def prepare(root: Path) -> None:
        path = root / "mkdocs.yml"
        config = yaml.safe_load(path.read_text(encoding="utf-8"))
        config["plugins"][0]["mkdoxy"]["projects"]["api"]["doxy-cfg"]["XML_PROGRAMLISTING"] = source_listing
        path.write_text(yaml.safe_dump(config), encoding="utf-8")

    project = build_project("navigation", options=BuildOptions(use_directory_urls=directory_urls), prepare=prepare)
    summary = project.markdown("links.md")
    targets = re.findall(r"\]\(([^)]+)\)", summary)
    index = ElementTree.parse(project.xml_dir / "index.xml")
    compounds = index.findall("compound")
    expected_kinds = {"namespace", "class", "struct", "group", "page", "file", "dir"}
    assert expected_kinds <= {node.get("kind") for node in compounds}
    for compound in compounds:
        if compound.get("kind") in expected_kinds:
            target = f"{compound.get('refid')}.md"
            assert targets.count(target) == 1, (compound.findtext("name"), summary)
    assert "[Namespace Member Enumerations](namespace_member_enums.md)" in summary
    assert "[Class Member Enumerations](class_member_enums.md)" in summary
    assert "NamespaceMode" in project.markdown("namespace_member_enums.md")
    assert "ClassMode" in project.markdown("class_member_enums.md")
    assert any(target.endswith("_source.md") for target in targets) == source_listing
    assert "Namespace ListNamespace List" not in summary

    page = Path("api/links/index.html" if directory_urls else "api/links.html")
    parser = _Links()
    parser.feed(project.html(page.as_posix()))
    html_targets = set()
    depths: dict[Path, int] = {}
    for href, depth in parser.hrefs:
        url = urlsplit(href)
        if not url.scheme and not url.netloc and not url.path.startswith("/"):
            target = (project.root / "site" / page.parent / unquote(url.path)).resolve()
            target = target / "index.html" if target.is_dir() else target
            html_targets.add(target)
            depths[target] = max(depth, depths.get(target, 0))
    for link in targets:
        assert (project.generated_dir / project.api_path / link).is_file(), link
        relative = Path(link).with_suffix("") if directory_urls else Path(link).with_suffix(".html")
        target = project.root / "site" / project.api_path / relative
        if directory_urls:
            target = target / "index.html"
        assert target.is_file(), link
        assert target.resolve() in html_targets, link

    def html_target(refid: str) -> Path:
        return (project.root / "site/api" / (f"{refid}/index.html" if directory_urls else f"{refid}.html")).resolve()

    for xml in project.xml_dir.glob("*.xml"):
        compound = ElementTree.parse(xml).find("compounddef")
        if compound is None:
            continue
        child_tags = {
            "namespace": ("innernamespace", "innerclass"),
            "class": ("innerclass",),
            "group": ("innergroup",),
            "dir": ("innerdir", "innerfile"),
        }.get(compound.get("kind"), ())
        for tag in child_tags:
            for child in compound.findall(tag):
                parent_target = html_target(compound.attrib["id"])
                child_target = html_target(child.attrib["refid"])
                assert depths[child_target] == depths[parent_target] + 1, (compound.attrib, child.attrib)


def test_page_and_group_titles_cannot_add_navigation_links(build_project: ProjectBuilder) -> None:
    title = "Guide](https://example.com/unintended) [Read more"

    def prepare(root: Path) -> None:
        header = root / "src/navigation.h"
        header.write_text(
            header.read_text(encoding="utf-8")
            .replace("top_module Top module", f"top_module {title}")
            .replace("overview Overview", f"overview {title}"),
            encoding="utf-8",
        )

    project = build_project("navigation", prepare=prepare)
    for refid in ("overview", "group__top__module"):
        # Keep the exact XML title as evidence that Doxygen did not remove it.
        xml = ElementTree.parse(project.xml_dir / f"{refid}.xml")
        assert xml.findtext("compounddef/title") == title
    parser = _Links()
    parser.feed(project.html("api/links/index.html"))
    assert not any("example.com/unintended" in href for href, _ in parser.hrefs)
    assert (project.root / "site/api/overview/index.html").is_file()
    assert (project.root / "site/api/group__top__module/index.html").is_file()
