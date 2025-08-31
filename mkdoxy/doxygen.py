import logging
import os
from xml.etree import ElementTree as ET

from mkdoxy.cache import Cache
from mkdoxy.constants import Kind, Visibility
from mkdoxy.node import Node
from mkdoxy.project import ProjectContext
from mkdoxy.xml_parser import XmlParser

log: logging.Logger = logging.getLogger("mkdocs")


class Doxygen:
    def __init__(self, index_path: str, parser: XmlParser, cache: Cache) -> None:
        self.debug = parser.debug
        path_xml = os.path.join(index_path, "index.xml")
        if self.debug:
            log.info("Loading XML from: %s", path_xml)
        xml = ET.parse(path_xml).getroot()

        self.parser = parser
        self.ctx = ProjectContext(cache)

        self.root = Node("root", None, self.ctx, self.parser, None)
        self.groups = Node("root", None, self.ctx, self.parser, None)
        self.files = Node("root", None, self.ctx, self.parser, None)
        self.pages = Node("root", None, self.ctx, self.parser, None)
        self.examples = Node("root", None, self.ctx, self.parser, None)

        for compound in xml.findall("compound"):
            kind = Kind.from_str(compound.get("kind"))
            refid = compound.get("refid")
            if kind.is_language():
                node = Node(
                    os.path.join(index_path, f"{refid}.xml"),
                    None,
                    self.ctx,
                    self.parser,
                    self.root,
                )
                node._visibility = Visibility.PUBLIC
                self.root.add_child(node)
            if kind == Kind.GROUP:
                node = Node(
                    os.path.join(index_path, f"{refid}.xml"),
                    None,
                    self.ctx,
                    self.parser,
                    self.root,
                )
                node._visibility = Visibility.PUBLIC
                self.groups.add_child(node)
            if kind in [Kind.FILE, Kind.DIR]:
                node = Node(
                    os.path.join(index_path, f"{refid}.xml"),
                    None,
                    self.ctx,
                    self.parser,
                    self.root,
                )
                node._visibility = Visibility.PUBLIC
                self.files.add_child(node)
            if kind == Kind.PAGE:
                node = Node(
                    os.path.join(index_path, f"{refid}.xml"),
                    None,
                    self.ctx,
                    self.parser,
                    self.root,
                )
                node._visibility = Visibility.PUBLIC
                self.pages.add_child(node)
            if kind == Kind.EXAMPLE:
                node = Node(
                    os.path.join(index_path, f"{refid}.xml"),
                    None,
                    self.ctx,
                    self.parser,
                    self.root,
                )
                node._visibility = Visibility.PUBLIC
                self.examples.add_child(node)

        if self.debug:
            log.info("Deduplicating data... (may take a minute!)")
        for child in self.root.children.copy():
            self._fix_duplicates(child, self.root, [])

        for child in self.groups.children.copy():
            self._fix_duplicates(child, self.groups, [Kind.GROUP])

        for child in self.files.children.copy():
            self._fix_duplicates(child, self.files, [Kind.FILE, Kind.DIR])

        for child in self.examples.children.copy():
            self._fix_duplicates(child, self.examples, [Kind.EXAMPLE])

        self._fix_parents(self.files)

        if self.debug:
            log.info("Sorting...")
        self._recursive_sort(self.root)
        self._recursive_sort(self.groups)
        self._recursive_sort(self.files)
        self._recursive_sort(self.pages)
        self._recursive_sort(self.examples)

    def _fix_parents(self, node: Node) -> None:
        if node.is_dir or node.is_root:
            for child in node.children:
                if child.is_file:
                    child._parent = node
                if child.is_dir:
                    self._fix_parents(child)

    def _recursive_sort(self, node: Node) -> None:
        node.sort_children()
        for child in node.children:
            self._recursive_sort(child)

    def _is_in_root(self, node: Node, root: Node) -> bool:
        return any(node.refid == child.refid for child in root.children)

    def _remove_from_root(self, refid: str, root: Node) -> None:
        for i, child in enumerate(root.children):
            if child.refid == refid:
                root.children.pop(i)
                return

    def _fix_duplicates(
        self, node: Node, root: Node, kind_filter: list[Kind]
    ) -> None:
        for child in node.children:
            if len(kind_filter) > 0 and child.kind not in kind_filter:
                continue
            if self._is_in_root(child, root):
                self._remove_from_root(child.refid, root)
            self._fix_duplicates(child, root, kind_filter)

    def print_structure(self) -> None:
        if not self.debug:
            return
        print("\n")
        log.info("Print root")
        for node in self.root.children:
            self.print_node(node, "")
        print("\n")

        log.info("Print groups")
        for node in self.groups.children:
            self.print_node(node, "")
        print("\n")

        log.info("Print files")
        for node in self.files.children:
            self.print_node(node, "")

    def print_node(self, node: Node, indent: str) -> None:
        if self.debug:
            log.info("%s %s %s", indent, node.kind, node.name)
        for child in node.children:
            self.print_node(child, indent + "  ")
