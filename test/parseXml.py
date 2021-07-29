import os
from lxml import etree
from typing import Dict
from beeprint import pp
import subprocess
import shlex


# os.walk


class DoxygenRun:
    def __init__(self, scriptSh, sourceDir, destinationDir):
        self.scriptSh = scriptSh
        self.destinationDir = destinationDir
        self.sourceDir = sourceDir
        self.command = f'{self.scriptSh} "Doxygn Snippets" {self.sourceDir} {self.destinationDir}'

    def run(self, print_command: bool = False):
        if print_command:
            print(self.command)
        subprocess.call(shlex.split(self.command))


class DoxygenParser:
    def __init__(self, doxygen_path: str):
        self.parsedXml = {}
        self.doxygen_path = doxygen_path
        # self.parsedXml = {}
        self.parsedXml["class"] = {}

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

    def getFilePath(self, filename: str) -> str:
        index_path = os.path.join(self.doxygen_path, filename)
        assert os.path.isfile(index_path)
        return index_path

    def getParsedXml(self) -> Dict[str, dict]:
        return self.parsedXml

    def parseIndex(self) -> None:
        # Find the index XML file
        index_path = self.getFilePath("index.xml")

        index_xml = etree.parse(source=index_path)
        for compound in index_xml.findall("compound"):
            kind = compound.attrib["kind"]
            if "class" in kind:
                self.parsedXml["class"][compound[0].text] = {"file": compound.get("refid")}

    def parseClasses(self) -> None:
        for doxyClass in self.parsedXml["class"]:
            class_path = self.getFilePath(f"{self.parsedXml['class'][doxyClass]['file']}.xml")
            class_xml = etree.parse(source=class_path).getroot()
            doxygen = class_xml.getchildren()[0]
            # self.parsedXml["class"][doxyClass]["language"] = doxygen.attrib["language"]
            self.parsedXml["class"][doxyClass]["compounddef"] = doxygen
            self.parsedXml["class"][doxyClass]["sectiondef"] = {}
            for compounddef in doxygen.getchildren():
                if compounddef.tag == "sectiondef":
                    self.parsedXml["class"][doxyClass]["sectiondef"][compounddef.get("kind")] = compounddef
                else:
                    self.parsedXml["class"][doxyClass][compounddef.tag] = compounddef


class DoxygenSnippets:
    def __init__(self, doxygenParser: DoxygenParser):
        self.doxygenParser = doxygenParser
        self.parsedXml = doxygenParser.parsedXml

    def getClass(self, name: str):
        return self.parsedXml["class"][name]

    def getClassesList(self):
        classList = []
        for name in self.parsedXml["class"]:
            classList.append(name)
        return classList


if __name__ == '__main__':
    runner = DoxygenRun("./extractDoxygen.sh",
                        "/media/kuba/neon/git/robo/rbcx-robotka/RB3204-RBCX-Doc/master/RB3204-RBCX-library/src/",
                        "/media/kuba/neon/git/robo/rbcx-robotka/RB3204-RBCX-Doc/master/RB3204-RBCX-library/doc/")
    # runner = DoxygenRun("./extractDoxygen.sh", "./cpp_basic/src/", "./cpp_basic/doc/")
    runner.run(print_command=True)

    parser = DoxygenParser('/media/kuba/neon/git/robo/rbcx-robotka/RB3204-RBCX-Doc/master/RB3204-RBCX-library/doc/xml/')
    # parser = DoxygenParser('cpp_basic/doc/xml/')
    parser.parseIndex()
    parser.parseClasses()

    pp(parser.getParsedXml())

    snippets = DoxygenSnippets(parser)
    print(snippets.getClassesList())

    # classCar = snippets.getClass("Car")
    # print(classCar)
