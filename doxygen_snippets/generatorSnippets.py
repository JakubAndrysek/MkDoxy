import os
from typing import *
from jinja2 import Template
from mkdocs.config import base
from mkdocs.structure import files, pages
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.finder import Finder

import string
import traceback
from typing import TextIO
from jinja2 import Template
from jinja2.exceptions import TemplateSyntaxError, TemplateError
from jinja2 import StrictUndefined, Undefined
from doxygen_snippets.node import Node, DummyNode
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.constants import Kind
from doxygen_snippets.generatorBase import GeneratorBase
import logging

logger = logging.getLogger("mkdocs")


class GeneratorSnippets:
	def __init__(self,
	             markdown,
	             generatorBase: GeneratorBase,
	             doxygen: Doxygen,
	             debug: bool = False):
		self.markdown = markdown
		self.generatorBase = generatorBase
		self.doxygen = doxygen
		self.debug = debug
		self.finder = Finder(doxygen, debug)

	def generate(self):
		mdTemplate = Template(self.markdown)
		# Register documentation generator callbacks
		return mdTemplate.render(
			doxyClass=self.doxyClass,
			doxyClassList=self.doxyClassList,
			doxyClassIndex=self.doxyClassIndex,
			doxyClassHierarchy=self.doxyClassHierarchy,
			doxyFunction=self.doxyFunction,
			doxyNamespaceList=self.doxyNamespaceList,
			doxyFileList=self.doxyFileList,
		)

	### Create documentation generator callbacks
	def doxyClass(self, className: str, methodeName: str = None, *args):
		node = self.finder.doxyClass(className, methodeName)
		if methodeName:
			if not node:
				return f"**Didnt find methode `{methodeName}` in Class `{className}`.**"
			md = self.generatorBase.function(node)
		else:
			if not node:
				return f"**Didn`t find Class `{className}`.**`"
			md = self.generatorBase.member(node)
		return md

	# return f"# Doxygen CLASS {className}-> {fClass.filename}"

	def doxyClassList(self):
		md = self.generatorBase.annotated(self.doxygen.root.children)
		return md

	def doxyClassIndex(self):
		md = self.generatorBase.classes(self.doxygen.root.children)
		return md

	def doxyClassHierarchy(self):
		md = self.generatorBase.hierarchy(self.doxygen.root.children)
		return md

	def doxyFunction(self, fileName: str, functionName: str, fullDoc: bool = True):
		functions = self.generatorBase.recursive_find_with_parent(self.doxygen.files.children, [Kind.FUNCTION], [Kind.FILE])
		return f"## Doxygen FUNCTION: {functionName}"

	def doxyNamespaceList(self):
		md = self.generatorBase.namespaces(self.doxygen.root.children)
		return md

	def doxyFileList(self):
		md = self.generatorBase.fileindex(self.doxygen.files.children)
		return md

### Create documentation generator callbacks END