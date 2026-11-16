from types import SimpleNamespace

from mkdoxy.constants import Kind
from mkdoxy.generatorAuto import GeneratorAuto


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
