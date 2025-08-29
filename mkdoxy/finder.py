from mkdoxy.constants import Kind
from mkdoxy.doxygen import Doxygen
from mkdoxy.utils import recursive_find, recursive_find_with_parent


class Finder:
    def __init__(self, doxygen: dict[str, Doxygen], debug: bool = False) -> None:
        self.doxygen = doxygen
        self.debug = debug

    def _normalize(self, name: str) -> str:
        return name.replace(" ", "")

    def list_to_names(self, list):
        return [part.name_params for part in list]

    def _doxy_parent(self, project, parent: str, kind: Kind):
        if not kind.is_parent():
            return None
        parents = recursive_find(self.doxygen[project].root.children, kind)
        if parents:
            for find_parent in parents:
                if find_parent.name_long == parent:
                    return find_parent
            return self.list_to_names(parents)
        return None

    def _doxy_member_in_parent(self, project, parent: str, parent_kind: Kind, member_name: str, member_kind: Kind):
        find_parent = self._doxy_parent(project, parent, parent_kind)
        if find_parent:
            if isinstance(find_parent, list):
                for member in find_parent:
                    if self._normalize(member_name) in self._normalize(member):
                        return member
                return find_parent
            else:
                members = recursive_find(find_parent.children, member_kind)
                if members:
                    for member in members:
                        if self._normalize(member_name) in self._normalize(member.name_params):
                            return member
                    return self.list_to_names(members)
                return None
        return None

    def doxy_class(self, project, class_name: str):
        return self._doxy_parent(project, class_name, Kind.CLASS)

    def doxy_namespace(self, project, namespace: str):
        return self._doxy_parent(project, namespace, Kind.NAMESPACE)

    def doxy_class_method(self, project, class_name: str, method_name: str):
        return self._doxy_member_in_parent(project, class_name, Kind.CLASS, method_name, Kind.FUNCTION)

    def doxy_namespace_function(self, project, namespace: str, function_name: str):
        return self._doxy_member_in_parent(project, namespace, Kind.NAMESPACE, function_name, Kind.FUNCTION)

    def doxy_function(self, project, function_name: str):
        functions = recursive_find_with_parent(self.doxygen[project].files.children, [Kind.FUNCTION], [Kind.FILE])
        if functions:
            for function in functions:
                if self._normalize(function_name) == self._normalize(function.name_params):
                    return function
            return self.list_to_names(functions)
        return None

    def doxy_code(self, project, file_name):
        files = recursive_find_with_parent(self.doxygen[project].files.children, [Kind.FILE], [Kind.DIR])
        if files:
            for file in files:
                if self._normalize(file_name) == self._normalize(file.name_long):
                    return file
            return self.list_to_names(files)
        return None