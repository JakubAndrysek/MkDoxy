from typing import Dict

from mkdoxy.constants import Kind
from mkdoxy.doxygen import Doxygen
from mkdoxy.node import Node


class Finder:
    def __init__(self, doxygen: Dict[str, Doxygen], debug: bool = False):
        self.doxygen = doxygen
        self.debug = debug

    @staticmethod
    def _normalize(name: str) -> str:
        return name.replace(" ", "")

    @staticmethod
    def list_to_names(list):
        return [part.name_params for part in list]

    def doxy_class(self, project, className: str):
        classes = recursive_find(self.doxygen[project].root.children, Kind.CLASS)
        if classes:
            for findClass in classes:
                if findClass.name_long == className:
                    return findClass
            return self.list_to_names(classes)
        return None

    def doxy_class_method(self, project, className: str, methodName: str):
        findClass = self.doxy_class(project, className)
        if findClass:
            if isinstance(findClass, list):
                for member in findClass:
                    if self._normalize(methodName) in self._normalize(member):
                        return member
                return findClass
            else:
                members = recursive_find(findClass.children, Kind.FUNCTION)
                if members:
                    for member in members:
                        if self._normalize(methodName) in self._normalize(member.name_params):
                            return member
                    return self.list_to_names(members)
                return None
        return None

    def doxy_function(self, project, functionName: str):
        functions = recursive_find_with_parent(self.doxygen[project].files.children, [Kind.FUNCTION], [Kind.FILE])
        if functions:
            for function in functions:
                if self._normalize(functionName) == self._normalize(function.name_params):
                    return function
            return self.list_to_names(functions)
        return None

    def doxy_code(self, project, fileName):
        files = recursive_find_with_parent(self.doxygen[project].files.children, [Kind.FILE], [Kind.DIR])
        if files:
            for file in files:
                if self._normalize(fileName) == self._normalize(file.name_long):
                    return file
            return self.list_to_names(files)
        return None


def recursive_find(nodes: list["Node"], kind: Kind) -> list["Node"]:
    ret = []
    for node in nodes:
        if node.kind == kind:
            ret.append(node)
        if node.kind.is_parent():
            ret.extend(recursive_find(node.children, kind))
    return ret


def recursive_find_with_parent(nodes: list["Node"], kinds: list[Kind], parent_kinds: list[Kind]) -> list["Node"]:
    ret: list["Node"] = []
    for node in nodes:
        if node.kind in kinds and node.parent is not None and node.parent.kind in parent_kinds:
            ret.append(node)
        if node.kind.is_parent() or node.kind.is_dir() or node.kind.is_file():
            ret.extend(recursive_find_with_parent(node.children, kinds, parent_kinds))
    return ret
