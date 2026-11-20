from html.parser import HTMLParser
from types import SimpleNamespace

import markdown
import pytest

from mkdoxy.constants import Kind
from mkdoxy.generatorAuto import GeneratorAuto, generate_link


def empty_tree():
    return SimpleNamespace(children=[])


def generate_links(tmp_path, doxygen=None) -> str:
    if doxygen is None:
        doxygen = SimpleNamespace(pages=empty_tree(), groups=empty_tree(), root=empty_tree(), files=empty_tree())
    generator = GeneratorAuto(
        generatorBase=SimpleNamespace(debug=False),
        tempDoxyDir=str(tmp_path),
        siteDir=str(tmp_path / "site"),
        apiPath="api",
        doxygen=doxygen,
        useDirectoryUrls=True,
    )

    generator.summary({})

    return (tmp_path / "api" / "links.md").read_text(encoding="utf-8")


def test_links_namespace_list_label(tmp_path):
    links = generate_links(tmp_path)

    assert "[Namespace List](namespaces.md)" in links
    assert "Namespace ListNamespace List" not in links


def test_links_top_level_items_are_not_indented(tmp_path):
    lines = generate_links(tmp_path).splitlines()

    assert lines
    assert [line for line in lines if not line.startswith("- [")] == []


def test_summary_retains_recursive_entries_in_order(tmp_path):
    def node(kind, name, *children):
        return SimpleNamespace(
            kind=kind, name=name, title=name, refid=name, children=list(children), has_programlisting=False
        )

    doxygen = SimpleNamespace(
        pages=SimpleNamespace(children=[node(Kind.PAGE, "Guide", node(Kind.PAGE, "Details"))]),
        groups=SimpleNamespace(children=[node(Kind.GROUP, "Module", node(Kind.GROUP, "Submodule"))]),
        root=SimpleNamespace(
            children=[node(Kind.NAMESPACE, "Outer", node(Kind.CLASS, "Child"), node(Kind.CLASS, "Sibling"))]
        ),
        files=SimpleNamespace(children=[node(Kind.DIR, "include", node(Kind.FILE, "header"))]),
    )
    output = generate_links(tmp_path, doxygen)
    for parent, child in (("Guide", "Details"), ("Module", "Submodule"), ("Outer", "Child"), ("include", "header")):
        assert output.count(f"]({parent}.md)") == 1
        assert output.count(f"]({child}.md)") == 1
        assert output.index(f"]({parent}.md)") < output.index(f"]({child}.md)")
    assert (
        "    - [namespace Outer](Outer.md)\n        - [class Child](Child.md)\n        - [class Sibling](Sibling.md)"
        in output
    )
    assert "_source.md" not in output


class _LabelLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str | None] = []
        self.text: list[str] = []
        self.in_link = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.hrefs.append(dict(attrs).get("href"))
            self.in_link = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self.in_link = False

    def handle_data(self, data: str) -> None:
        if self.in_link:
            self.text.append(data)


@pytest.mark.parametrize(
    "title",
    [
        "Guide](https://example.com/unintended) [Read more",
        "Backslash\\](https://example.com/unintended) [label",
        "<a href='https://example.com/unintended'>HTML</a>",
        "<https://example.com/unintended>",
        "__private__ *literal* `code` [brackets] & entities &#93;",
        "First line\nSecond line",
    ],
)
def test_generated_link_labels_are_literal_text(title: str) -> None:
    parser = _LabelLinks()
    parser.feed(markdown.markdown(generate_link(title, "expected.md")))
    assert parser.hrefs == ["expected.md"]
    assert "".join(parser.text) == " ".join(title.splitlines())
