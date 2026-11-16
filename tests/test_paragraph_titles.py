"""Regression checks for empty and formatted simple-section titles."""

from xml.etree.ElementTree import fromstring

import pytest

from mkdoxy.cache import Cache
from mkdoxy.xml_parser import XmlParser


@pytest.mark.parametrize("title", ["", "<title/>", "<title> \n </title>", "<title><bold/> </title>"])
def test_empty_paragraph_title_has_no_empty_emphasis(title: str) -> None:
    xml = fromstring(f'<para><simplesect kind="par">{title}<para>Body.</para></simplesect></para>')
    output = XmlParser(Cache()).paras_as_str(xml)
    assert output.strip() == "Body."
    assert "**" not in output


@pytest.mark.parametrize(
    "title, expected",
    [
        ("<title> Tip: </title>", "**Tip:**"),
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
