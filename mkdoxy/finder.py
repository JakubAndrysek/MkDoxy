from typing import Dict

from mkdoxy.constants import Kind
from mkdoxy.doxygen import Doxygen
from mkdoxy.utils import recursive_find, recursive_find_with_parent


class Finder:
    def __init__(self, doxygen: Dict[str, Doxygen], debug: bool = False):
        self.doxygen = doxygen
        self.debug = debug

    def _normalize(self, name: str) -> str:
        return name.replace(" ", "")

    def listToNames(self, list):
        return [part.name_params for part in list]

    def _doxyParent(self, project, parent: str, kind: Kind):
        if not kind.is_parent():
            return None
        parents = recursive_find(self.doxygen[project].root.children, kind)
        if parents:
            for findParent in parents:
                if findParent.name_long == parent:
                    return findParent
            return self.listToNames(parents)
        return None

    def _doxyMemberInParent(self, project, parent: str, parentKind: Kind, memberName: str, memberKind: Kind):
        findParent = self._doxyParent(project, parent, parentKind)
        if findParent:
            if isinstance(findParent, list):
                for member in findParent:
                    if self._normalize(memberName) in self._normalize(member):
                        return member
                return findParent
            else:
                members = recursive_find(findParent.children, memberKind)
                if members:
                    for member in members:
                        if self._normalize(memberName) in self._normalize(member.name_params):
                            return member
                    return self.listToNames(members)
                return None
        return None

    def doxyClass(self, project, className: str):
        return self._doxyParent(project, className, Kind.CLASS)

    def doxyNamespace(self, project, namespace: str):
        return self._doxyParent(project, namespace, Kind.NAMESPACE)

    def doxyClassMethod(self, project, className: str, methodName: str):
        return self._doxyMemberInParent(project, className, Kind.CLASS, methodName, Kind.FUNCTION)

    def doxyNamespaceFunction(self, project, namespace: str, functionName: str):
        return self._doxyMemberInParent(project, namespace, Kind.NAMESPACE, functionName, Kind.FUNCTION)

    def doxyFunction(self, project, functionName: str):
        functions = recursive_find_with_parent(self.doxygen[project].files.children, [Kind.FUNCTION], [Kind.FILE])
        if functions:
            for function in functions:
                if self._normalize(functionName) == self._normalize(function.name_params):
                    return function
            return self.listToNames(functions)
        return None

    def doxyCode(self, project, fileName):
        files = recursive_find_with_parent(self.doxygen[project].files.children, [Kind.FILE], [Kind.DIR])
        if files:
            for file in files:
                if self._normalize(fileName) == self._normalize(file.name_long):
                    return file
            return self.listToNames(files)
        return None
