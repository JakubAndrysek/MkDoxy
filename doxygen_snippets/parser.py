import os
from typing import Dict
from jinja2 import Template

from lxml import etree
from mkdocs.config import base
from mkdocs.structure import files, pages
import logging

logger = logging.getLogger("mkdocs")


class DoxygenParser:
    def __init__(self, doxygen_path: str):
        self.parsedXml = {}
        self.doxygen_path = doxygen_path
        # self.parsedXml = {}
        self.parsedXml["class"] = {}

    def getFilePath(self, filename: str) -> str:
        relative = os.path.join(os.path.join(self.doxygen_path, "xml"), filename)
        index_path = os.path.abspath(relative)
        logger.error(index_path)
        assert os.path.isfile(index_path)
        return index_path

    def getParsedXml(self) -> Dict[str, dict]:
        return self.parsedXml

    def parseIndex(self) -> None:
        index_path = self.getFilePath("index.xml")

        index_xml = etree.parse(source=index_path)
        for compound in index_xml.findall("compound"):
            kind = compound.attrib["kind"]
            if "class" in kind:
                self.parsedXml["class"][compound[0].text] = {"file": compound.get("refid")}

    # def run(self, root: Element):  # noqa: D102 (ignore missing docstring)
    #     if not self.id_prefix:
    #         return
    #     for el in root.iter():
    #         id_attr = el.get("id")
    #         if id_attr:
    #             el.set("id", self.id_prefix + id_attr)
    #
    #         href_attr = el.get("href")
    #         if href_attr and href_attr.startswith("#"):
    #             el.set("href", "#" + self.id_prefix + href_attr[1:])
    #
    #         name_attr = el.get("name")
    #         if name_attr:
    #             el.set("name", self.id_prefix + name_attr)
    #
    #         if el.tag == "label":
    #             for_attr = el.get("for")
    #             if for_attr:
    #                 el.set("for", self.id_prefix + for_attr)
