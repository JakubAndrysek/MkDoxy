"""Regression checks for empty and formatted simple-section titles."""

from types import SimpleNamespace
from xml.etree.ElementTree import fromstring

import pytest

from mkdoxy.cache import Cache
from mkdoxy.xml_parser import XmlParser


@pytest.mark.parametrize(
    "title",
    [
        "",
        "<title/>",
        "<title> \n </title>",
        "<title><bold/> </title>",
        "<title><emphasis> </emphasis><computeroutput> </computeroutput></title>",
    ],
)
def test_empty_paragraph_title_has_no_empty_emphasis(title: str) -> None:
    xml = fromstring(f'<para><simplesect kind="par">{title}<para>Body.</para></simplesect></para>')
    output = XmlParser(Cache()).paras_as_str(xml)
    assert output.strip() == "Body."
    assert "**" not in output


@pytest.mark.parametrize(
    "title, expected",
    [
        ("<title> Tip: </title>", "**Tip:**"),
        ("<title><emphasis><bold>NestedTitle</bold></emphasis></title>", "**_NestedTitle_**"),
        ("<title><emphasis> ItalicTitle </emphasis></title>", "**_ItalicTitle_**"),
        ("<title><computeroutput> CodeTitle </computeroutput></title>", "**`CodeTitle`**"),
        ("<title><emphasis> </emphasis>Visible<computeroutput> </computeroutput></title>", "**Visible**"),
        ("<title>Before <emphasis>middle words</emphasis> after</title>", "**Before _middle words_ after**"),
        ("<title><bold>BoldTitle</bold> </title>", "**BoldTitle**"),
        ("<title>Before <bold>BoldWord</bold> after</title>", "**Before BoldWord after**"),
        ("<title><emphasis>ItalicTitle</emphasis> </title>", "**_ItalicTitle_**"),
        ("<title><computeroutput>CodeTitle</computeroutput> </title>", "**`CodeTitle`**"),
    ],
)
def test_formatted_title_preserves_inline_content(title: str, expected: str) -> None:
    xml = fromstring(f'<para><simplesect kind="par">{title}<para>Body.</para></simplesect></para>')
    output = XmlParser(Cache()).paras_as_str(xml)
    assert output.strip() == f"{expected}\n\nBody."


@pytest.mark.parametrize("kind, label", [("note", "Note:"), ("warning", "Warning:"), ("see", "See also:")])
def test_standard_simple_sections_keep_existing_labels(kind: str, label: str) -> None:
    xml = fromstring(f'<para><simplesect kind="{kind}"><para>Body.</para></simplesect></para>')
    output = XmlParser(Cache()).paras_as_str(xml)
    separator = " " if kind == "see" else "\n\n"
    assert output.strip() == f"**{label}**{separator}Body."


@pytest.mark.parametrize("label", ["", "Widget"])
def test_reference_title_resolves_name_without_nested_emphasis(label: str) -> None:
    cache = Cache()
    cache.add("widget", SimpleNamespace(url="classWidget.md", get_full_name=lambda: "Widget"))
    xml = fromstring(
        f'<para><simplesect kind="par"><title><ref refid="widget">{label}</ref></title>'
        "<para>Body.</para></simplesect></para>"
    )
    assert XmlParser(cache).paras_as_str(xml).strip() == "**[Widget](classWidget.md)**\n\nBody."
