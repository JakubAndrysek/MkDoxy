from __future__ import annotations

import logging
import os

from mkdocs.structure import files

from mkdoxy.constants import Kind
from mkdoxy.doxygen import Doxygen
from mkdoxy.generatorBase import GeneratorBase
from mkdoxy.node import Node

log: logging.Logger = logging.getLogger("mkdocs")

ADDITIONAL_FILES = {
    "Namespace ListNamespace List": "namespaces.md",
    "Namespace Members": "namespace_members.md",
    "Namespace Member Functions": "namespace_member_functions.md",
    "Namespace Member Variables": "namespace_member_variables.md",
    "Namespace Member Typedefs": "namespace_member_typedefs.md",
    "Namespace Member Enumerations": "namespace_member_enums.md",
    "Class Index": "classes.md",
    "Class Hierarchy": "hierarchy.md",
    "Class Members": "class_members.md",
    "Class Member Functions": "class_member_functions.md",
    "Class Member Variables": "class_member_variables.md",
    "Class Member Typedefs": "class_member_typedefs.md",
    "Class Member Enumerations": "class_member_enums.md",
}


def generate_link(name: str, url: str, end: str = "\n") -> str:
    def normalize(name: str) -> str:
        return "\\" + name if name.startswith("__") else name

    return f"- [{normalize(name)}]({url}){end}"


# def generate_link(name, url) -> str:
# 	return f"\t\t- '{name}': '{url}'\n"


class GeneratorAuto:
    def __init__(
        self,
        generator_base: GeneratorBase,
        temp_doxy_dir: str,
        site_dir: str,
        api_path: str,
        doxygen: Doxygen,
        use_directory_urls: bool,
    ) -> None:
        self.generator_base = generator_base
        self.temp_doxy_dir = temp_doxy_dir
        self.site_dir = site_dir
        self.api_path = api_path
        self.doxygen = doxygen
        self.use_directory_urls = use_directory_urls
        self.full_doc_files: list[files.File] = []
        self.debug = generator_base.debug
        os.makedirs(os.path.join(self.temp_doxy_dir, self.api_path),
                    exist_ok=True)

    def save(self, path: str, output: str) -> None:
        path_rel = os.path.join(self.api_path, path)
        self.full_doc_files.append(
            files.File(path_rel, self.temp_doxy_dir, self.site_dir, self.use_directory_urls))
        with open(os.path.join(self.temp_doxy_dir, path_rel), "w", encoding="utf-8") as file:
            file.write(output)

    def full_doc(self, default_template_config: dict) -> None:
        self.annotated(self.doxygen.root.children, default_template_config)
        self.fileindex(self.doxygen.files.children, default_template_config)
        self.members(self.doxygen.root.children, default_template_config)
        self.members(self.doxygen.groups.children, default_template_config)
        self.files(self.doxygen.files.children, default_template_config)
        self.namespaces(self.doxygen.root.children, default_template_config)
        self.classes(self.doxygen.root.children, default_template_config)
        self.hierarchy(self.doxygen.root.children, default_template_config)
        self.modules(self.doxygen.groups.children, default_template_config)
        self.pages(self.doxygen.pages.children, default_template_config)
        # self.examples(self.doxygen.examples.children) # TODO examples
        self.relatedpages(self.doxygen.pages.children)
        self.index(
            self.doxygen.root.children,
            [Kind.FUNCTION, Kind.VARIABLE, Kind.TYPEDEF, Kind.ENUM],
            [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
            "Class Members",
            default_template_config,
        )
        self.index(
            self.doxygen.root.children,
            [Kind.FUNCTION],
            [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
            "Class Member Functions",
            default_template_config,
        )
        self.index(
            self.doxygen.root.children,
            [Kind.VARIABLE],
            [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
            "Class Member Variables",
            default_template_config,
        )
        self.index(
            self.doxygen.root.children,
            [Kind.TYPEDEF],
            [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
            "Class Member Typedefs",
            default_template_config,
        )
        self.index(
            self.doxygen.root.children,
            [Kind.ENUM],
            [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
            "Class Member Enums",
            default_template_config,
        )
        self.index(
            self.doxygen.root.children,
            [Kind.FUNCTION, Kind.VARIABLE, Kind.TYPEDEF, Kind.ENUM],
            [Kind.NAMESPACE],
            "Namespace Members",
            default_template_config,
        )
        self.index(
            self.doxygen.root.children,
            [Kind.FUNCTION],
            [Kind.NAMESPACE],
            "Namespace Member Functions",
            default_template_config,
        )
        self.index(
            self.doxygen.root.children,
            [Kind.VARIABLE],
            [Kind.NAMESPACE],
            "Namespace Member Variables",
            default_template_config,
        )
        self.index(
            self.doxygen.root.children,
            [Kind.TYPEDEF],
            [Kind.NAMESPACE],
            "Namespace Member Typedefs",
            default_template_config,
        )
        self.index(
            self.doxygen.root.children,
            [Kind.ENUM],
            [Kind.NAMESPACE],
            "Namespace Member Enums",
            default_template_config,
        )
        self.index(
            self.doxygen.files.children,
            [Kind.FUNCTION],
            [Kind.FILE],
            "Functions",
            default_template_config,
        )
        self.index(
            self.doxygen.files.children,
            [Kind.DEFINE],
            [Kind.FILE],
            "Macros",
            default_template_config,
        )
        self.index(
            self.doxygen.files.children,
            [Kind.VARIABLE, Kind.UNION, Kind.TYPEDEF, Kind.ENUM],
            [Kind.FILE],
            "Variables",
            default_template_config,
        )

    def annotated(self, nodes: list[Node], config: dict | None = None) -> None:
        path = "annotated.md"
        output = self.generator_base.annotated(nodes, config)
        self.save(path, output)

    def programlisting(self, node: Node, config: dict | None = None) -> None:
        path = f"{node.refid}_source.md"

        output = self.generator_base.programlisting(node, config)
        self.save(path, output)

    def fileindex(self, nodes: list[Node], config: dict | None = None) -> None:
        path = "files.md"

        output = self.generator_base.fileindex(nodes, config)
        self.save(path, output)

    def namespaces(self, nodes: list[Node], config: dict | None = None) -> None:
        path = "namespaces.md"

        output = self.generator_base.namespaces(nodes, config)
        self.save(path, output)

    def page(self, node: Node, config: dict | None = None) -> None:
        path = f"{node.name}.md"

        output = self.generator_base.page(node, config)
        self.save(path, output)

    def pages(self, nodes: list[Node], config: dict | None = None) -> None:
        for node in nodes:
            self.page(node, config)

    def relatedpages(self, nodes: list[Node], config: dict | None = None) -> None:
        path = "pages.md"

        output = self.generator_base.relatedpages(nodes)
        self.save(path, output)

    def example(self, node: Node, config: dict | None = None) -> None:
        path = f"{node.refid}.md"

        output = self.generator_base.example(node, config)
        self.save(path, output)

    def examples(self, nodes: list[Node], config: dict | None = None) -> None:
        for node in nodes:
            if node.is_example:
                if node.has_programlisting:
                    print(f"Generating example {node.name}...")
                self.example(node, config)

        path = "examples.md"

        output = self.generator_base.examples(nodes, config)
        self.save(path, output)

    def classes(self, nodes: list[Node], config: dict | None = None) -> None:
        path = "classes.md"

        output = self.generator_base.classes(nodes, config)
        self.save(path, output)

    def modules(self, nodes: list[Node], config: dict | None = None) -> None:
        path = "modules.md"

        output = self.generator_base.modules(nodes, config)
        self.save(path, output)

    def hierarchy(self, nodes: list[Node], config: dict | None = None) -> None:
        path = "hierarchy.md"

        output = self.generator_base.hierarchy(nodes, config)
        self.save(path, output)

    def member(self, node: Node, config: dict | None = None) -> None:
        path = node.filename

        output = self.generator_base.member(node, config)
        self.save(path, output)

        if node.is_language or node.is_group or node.is_file or node.is_dir:
            self.members(node.children, config)

    def file(self, node: Node, config: dict | None = None) -> None:
        path = node.filename

        output = self.generator_base.file(node, config)
        self.save(path, output)

        if node.is_file and node.has_programlisting:
            self.programlisting(node, config)

        if node.is_file or node.is_dir:
            self.files(node.children, config)

    def members(self, nodes: list[Node], config: dict | None = None) -> None:
        for node in nodes:
            if node.is_parent or node.is_group or node.is_file or node.is_dir:
                self.member(node, config)

    def files(self, nodes: list[Node], config: dict | None = None) -> None:
        for node in nodes:
            if node.is_file or node.is_dir:
                self.file(node, config)

    def index(
        self,
        nodes: list[Node],
        kind_filters: list[Kind],
        kind_parents: list[Kind],
        title: str,
        config: dict | None = None,
    ) -> None:
        path = title.lower().replace(" ", "_") + ".md"

        output = self.generator_base.index(
            nodes, kind_filters, kind_parents, title, config
        )
        self.save(path, output)

    def _generate_recursive(self, output_summary: str, node: Node, level: int) -> None:
        if node.kind.is_parent():
            output_summary += str(" " * level + generate_link(f"{node.kind.value} {node.name}", f"{node.refid}.md"))
            for child in node.children:
                self._generate_recursive(output_summary, child, level + 2)

    def _generate_recursive_files(
        self, output_summary: str, node: Node, level: int, config: dict | None = None
    ) -> None:
        if config is None:
            config = {}
        if node.kind.is_file() or node.kind.is_dir():
            output_summary += str(" " * int(level + 2) + generate_link(node.name, f"{node.refid}.md", end=""))

            if node.kind.is_file():
                output_summary += f" [[source code]]({node.refid}_source.md) \n"
            else:
                output_summary += "\n"

            for child in node.children:
                self._generate_recursive_files(output_summary, child, level + 2, config)

    def _generate_recursive_examples(self, output_summary: str, node: Node, level: int) -> None:
        if node.kind.is_example():
            output_summary += str(" " * level + generate_link(node.name, f"{node.refid}.md"))
            for child in node.children:
                self._generate_recursive_examples(output_summary, child, level + 2)

    def _generate_recursive_groups(self, output_summary: str, node: Node, level: int) -> None:
        if node.kind.is_group():
            output_summary += str(" " * level + generate_link(node.title, f"{node.refid}.md"))
            for child in node.children:
                self._generate_recursive_groups(output_summary, child, level + 2)

    def _generate_recursive_pages(self, output_summary: str, node: Node, level: int) -> None:
        if node.kind.is_page():
            output_summary += str(" " * level + generate_link(node.title, f"{node.refid}.md"))
            for child in node.children:
                self._generate_recursive_pages(output_summary, child, level + 2)

    def summary(self, default_template_config: dict) -> None:
        offset = 0
        output_summary = "" + str(" " * (offset + 2) + generate_link("Related Pages", "pages.md"))
        for node in self.doxygen.pages.children:
            self._generate_recursive_pages(output_summary, node, offset + 4)

        output_summary += str(" " * (offset + 2) + generate_link("Modules", "modules.md"))
        for node in self.doxygen.groups.children:
            self._generate_recursive_groups(output_summary, node, offset + 4)

        output_summary += str(" " * (offset + 2) + generate_link("Class List", "annotated.md"))
        for node in self.doxygen.root.children:
            self._generate_recursive(output_summary, node, offset + 4)

        for key, val in ADDITIONAL_FILES.items():
            output_summary += str(" " * (offset + 2) + generate_link(key, val))

        output_summary += str(" " * (offset + 2) + generate_link("Files", "files.md", end="\n"))
        for node in self.doxygen.files.children:
            self._generate_recursive_files(output_summary, node, offset + 4, default_template_config)

        # output_summary += str(' ' * (offset + 2) + generate_link('Examples', 'examples.md'))
        # for node in self.doxygen.examples.children:
        # 	self._generate_recursive_examples(node, offset + 4)

        output_summary += str(" " * (offset + 2) + generate_link("File Variables", "variables.md"))
        output_summary += str(" " * (offset + 2) + generate_link("File Functions", "functions.md"))
        output_summary += str(" " * (offset + 2) + generate_link("File Macros", "macros.md"))

        self.save("links.md", output_summary)
