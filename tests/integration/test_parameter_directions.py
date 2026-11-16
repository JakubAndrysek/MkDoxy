"""Check Doxygen input and actual generated Markdown/HTML, not only build success."""

import re
from html import unescape
from typing import Callable
from xml.etree import ElementTree

import pytest

from .project import BuiltProject

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def directions(build_project: Callable[[str], BuiltProject]) -> BuiltProject:
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
    assert "api/classDirectionExample/" in directions.html("index.html")


@pytest.mark.xfail(strict=True, reason="Known missing parameter directions: issue #78 / PR #147", raises=AssertionError)
@pytest.mark.parametrize("name,direction", [("source", "in"), ("destination", "out"), ("state", "in/out")])
def test_parameter_directions(directions: BuiltProject, name: str, direction: str) -> None:
    markdown = directions.markdown("classDirectionExample.md")
    html = directions.html("api/classDirectionExample/index.html")
    assert re.search(rf"\[{re.escape(direction)}\]\s+`{name}`", markdown)
    text = unescape(re.sub(r"<[^>]+>", "", html))
    assert re.search(rf"\[{re.escape(direction)}\]\s+{name}\b", text)
