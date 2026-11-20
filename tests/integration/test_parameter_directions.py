"""Check Doxygen input and actual generated Markdown/HTML, not only build success."""

import re
from html import unescape
from html.parser import HTMLParser
from xml.etree import ElementTree

import pytest

from .project import BuiltProject, ProjectBuilder

pytestmark = pytest.mark.integration


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.href: str | None = None
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.text = []

    def handle_data(self, data: str) -> None:
        if self.href is not None:
            self.text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.href is not None:
            self.links.append(("".join(self.text).strip(), self.href))
            self.href = None


@pytest.fixture(scope="module")
def directions(build_project: ProjectBuilder) -> BuiltProject:
    return build_project("parameter_directions")


def test_parameter_documentation(directions: BuiltProject) -> None:
    parameters = {}
    for xml in directions.xml_dir.glob("*.xml"):
        for node in ElementTree.parse(xml).findall(".//parametername"):
            parameters[node.text] = node.get("direction")
    assert parameters == {"source": "in", "destination": "out", "state": "inout", "plain": None}

    markdown = directions.markdown("classDirectionExample.md")
    html = directions.html("api/classDirectionExample/index.html")
    for name, description in (
        ("source", "Input value to read."),
        ("destination", "Output value to write."),
        ("state", "State value to update."),
        ("plain", "Value without a direction annotation."),
    ):
        assert f"`{name}` {description}" in markdown
        assert f"<code>{name}</code> {description}" in html
    assert not re.search(r"\[(?:in|out|in/out)\]\s+`plain`", markdown)
    links = _LinkParser()
    links.feed(directions.html("index.html"))
    # Check the fixture's actual link, not a matching navigation entry or text.
    hrefs = [href for label, href in links.links if label == "generated API"]
    assert hrefs == ["api/classDirectionExample/"]
    linked_page = directions.root / "site" / hrefs[0] / "index.html"
    assert linked_page.is_file()
    assert linked_page.read_text(encoding="utf-8") == html


@pytest.mark.parametrize("name,direction", [("source", "in"), ("destination", "out"), ("state", "in/out")])
def test_parameter_directions(directions: BuiltProject, name: str, direction: str) -> None:
    markdown = directions.markdown("classDirectionExample.md")
    html = directions.html("api/classDirectionExample/index.html")
    assert re.search(rf"\[{re.escape(direction)}\]\s+`{name}`", markdown)
    text = unescape(re.sub(r"<[^>]+>", "", html))
    assert re.search(rf"\[{re.escape(direction)}\]\s+{name}\b", text)


def test_parameter_directions_in_method_snippet(directions: BuiltProject) -> None:
    html = directions.html("snippet/index.html")
    assert "::: doxy." not in html
    text = unescape(re.sub(r"<[^>]+>", "", html))
    for name, direction, description in (
        ("source", "in", "Input value to read."),
        ("destination", "out", "Output value to write."),
        ("state", "in/out", "State value to update."),
    ):
        assert re.search(rf"\[{re.escape(direction)}\]\s+{name}\b", text)
        assert f"<code>{name}</code> {description}" in html
    assert "<code>plain</code> Value without a direction annotation." in html
    assert not re.search(r"\[(?:in|out|in/out)\]\s+plain\b", text)
