from types import SimpleNamespace

from mkdoxy.generatorAuto import GeneratorAuto


def empty_tree():
    return SimpleNamespace(children=[])


def generate_links(tmp_path) -> str:
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
