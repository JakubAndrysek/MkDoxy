"""Custom paragraph titles survive Doxygen XML, Markdown and HTML rendering."""

from html.parser import HTMLParser
from xml.etree import ElementTree

import pytest

from .project import ProjectBuilder

pytestmark = pytest.mark.integration


class _StrongParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.labels: list[str] = []
        self.depth = 0
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "strong":
            if self.depth == 0:
                self.text = []
            self.depth += 1

    def handle_data(self, data: str) -> None:
        if self.depth:
            self.text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "strong":
            self.depth -= 1
            if self.depth == 0:
                self.labels.append("".join(self.text).strip())


def test_paragraph_titles_reach_html(build_project: ProjectBuilder) -> None:
    project = build_project("paragraph_titles")
    titles = [
        title
        for xml in project.xml_dir.glob("*.xml")
        for title in ElementTree.parse(xml).findall(".//simplesect[@kind='par']/title")
    ]
    bold = next(title for title in titles if "".join(title.itertext()).strip() == "BoldTitle")
    assert not (bold.text or "").strip()
    assert bold.find("bold") is not None
    markdown = project.markdown("classParagraphExample.md")
    html = project.html("api/classParagraphExample/index.html")
    parser = _StrongParser()
    parser.feed(html)
    for title in (
        "Tip:",
        "BoldTitle",
        "Before BoldWord after",
        "ItalicTitle",
        "CodeTitle",
        "NestedTitle",
        "PaddedTitle",
        "PaddedCode",
    ):
        assert parser.labels.count(title) == 1, (title, parser.labels)
    for body in ("Plain", "Bold", "Mixed", "Italic", "Code", "Nested", "Padded", "Padded code", "Untitled"):
        assert f"{body} paragraph body." in markdown
        assert f"{body} paragraph body." in html
    assert "**Tip:**" in markdown
    assert "**BoldTitle**" in markdown
    assert "**Before BoldWord after**" in markdown
    assert "<em>ItalicTitle</em>" in html
    assert "<code>CodeTitle</code>" in html
    assert "<strong><em>NestedTitle</em></strong>" in html
    assert "<strong><em>PaddedTitle</em></strong>" in html
    assert "<strong><code>PaddedCode</code></strong>" in html
    assert "****" not in markdown
    for label in ("Note:", "Warning:", "See also:"):
        assert label in parser.labels
    assert "Standard note body." in html
    assert "Standard warning body." in html
    assert '<a href="./"><strong>ParagraphExample</strong></a>' in html
