import os
import re
import string
import traceback
from typing import TextIO
from jinja2 import Template
from jinja2.exceptions import TemplateSyntaxError, TemplateError
from jinja2 import StrictUndefined, Undefined
from doxygen_snippets.node import Node, DummyNode
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.constants import Kind
from pprint import pp


class Finder:
	def __init__(self, doxygen: Doxygen, debug: bool = False):
		self.doxygen = doxygen
		self.debug = debug

	def _recursive_find(self, nodes: [Node], kind: Kind):
		ret = []
		for node in nodes:
			if node.kind == kind:
				ret.append(node)
			if node.kind.is_parent():
				ret.extend(self._recursive_find(node.children, kind))
		return ret

	def _recursive_find_with_parent(self, nodes: [Node], kinds: [Kind], parent_kinds: [Kind]):
		ret = []
		for node in nodes:
			if node.kind in kinds and node.parent is not None and node.parent.kind in parent_kinds:
				ret.append(node)
			if node.kind.is_parent() or node.kind.is_dir() or node.kind.is_file():
				ret.extend(self._recursive_find_with_parent(node.children, kinds, parent_kinds))
		return ret

	def _normalize(self, name: str) -> str:
		return name.replace(" ", "")

	def doxyClass(self, className: str, functionName=None):
		classes = self._recursive_find(self.doxygen.root.children, Kind.CLASS)
		for findClass in classes:
			if findClass.name_long == className:
				if functionName:
					members = self._recursive_find(findClass.children, Kind.FUNCTION)
					for member in members:
						if self._normalize(functionName) in self._normalize(member.name_params):
							return member
				else:
					return findClass
		return None

	def doxyFunction(self, functionName: str):
		if functionName:
			functions = self._recursive_find_with_parent(self.doxygen.files.children, [Kind.FUNCTION], [Kind.FILE])
			for function in functions:
				if self._normalize(functionName) == self._normalize(function.name_params):
					return function
		return None