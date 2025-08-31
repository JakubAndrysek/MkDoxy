
from __future__ import annotations

from mkdoxy.constants import Kind
from mkdoxy.doxygen import Doxygen
from mkdoxy.utils import recursive_find, recursive_find_with_parent


class Finder:
    def __init__(self, doxygen: dict[str, Doxygen],
                 debug: bool = False) -> None:
        self.doxygen = doxygen
        self.debug = debug

    def _normalize(self, name: str) -> str:
        return name.replace(" ", "")

    def list_to_names(self, items: list) -> list[str]:
        return [part.name_params for part in items]

    def _doxy_parent(self, project: str, parent: str,
                     kind: Kind) -> list[str] | None:
        if not kind.is_parent():
            return None
        parents = recursive_find(self.doxygen[project].root.children, kind)
        if parents:
            for find_parent in parents:
                if find_parent.name_long == parent:
                    return find_parent
            return self.list_to_names(parents)
        return None

    def _doxy_member_in_parent(self, project: str, parent: str,
                              parent_kind: Kind, member_name: str,
                              member_kind: Kind) -> list[str] | None:
        find_parent = self._doxy_parent(project, parent, parent_kind)
        if find_parent is None:
            return None
        if isinstance(find_parent, list):
            for member in find_parent:
                if self._normalize(member_name) in self._normalize(member):
                    return member
            return find_parent
        else:
            members = recursive_find(find_parent.children, member_kind)
            if members:
                for member in members:
                    if member.name_params == member_name:
                        return member
                return self.list_to_names(members)
        return None

    def doxy_class(self, project: str, class_name: str) -> list[str] | None:
        return self._doxy_parent(project, class_name, Kind.CLASS)

    def doxy_namespace(self, project: str, namespace: str) -> list[str] | None:
        return self._doxy_parent(project, namespace, Kind.NAMESPACE)

    def doxy_class_method(self, project: str, class_name: str,
                          method_name: str) -> list[str] | None:
        return self._doxy_member_in_parent(project, class_name, Kind.CLASS,
                                           method_name, Kind.FUNCTION)

    def doxy_namespace_function(self, project: str, namespace: str,
                                function_name: str) -> list[str] | None:
        return self._doxy_member_in_parent(project, namespace, Kind.NAMESPACE,
                                           function_name, Kind.FUNCTION)

    def doxy_function(self, project: str,
                      function_name: str) -> list[str] | None:
        functions = recursive_find_with_parent(
            self.doxygen[project].files.children, [Kind.FUNCTION], [Kind.FILE]
        )
        if functions:
            for function in functions:
                if function.name_params == function_name:
                    return function
            return self.list_to_names(functions)
        return None

    def doxy_code(self, project: str, file_name: str) -> list[str] | None:
        files = recursive_find(self.doxygen[project].files.children, Kind.FILE)
        if files:
            for file in files:
                if file.name_params == file_name:
                    return file
            return self.list_to_names(files)
        return None
