import os
import sys
from typing import *
from jinja2 import Template
from mkdocs.config import base
from mkdocs.structure import files, pages
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.finder import Finder
import re
from ruamel.yaml import YAML, YAMLError
from pprint import *

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

regex = r"(?s)(?<!```yaml\n)(^::: doxy.(?P<key>[a-zA-Z.-_]+))\s*\n(?P<yaml>.*?)(?:(?:(?:\r*\n)(?=\n))|(?=:::)|`|\Z)"

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
		matches = re.finditer(regex, self.markdown, re.MULTILINE)
		for match in reversed(list(matches)):
			key = match.group('key')
			yamlRaw = match.group('yaml')
			if yamlRaw:
				try:
					yaml = YAML()
					config = yaml.load(yamlRaw)
					yaml.dump(config, sys.stdout)
				except YAMLError as e:
					print(e)

			keyLow = key.lower()
			print(f"Key: {keyLow}")
			if keyLow.startswith("class"):
				if keyLow.endswith("list"):
					replaceStr = self.doxyClassList()
				elif keyLow.endswith("index"):
					replaceStr = self.doxyClassIndex()
				else:
					replaceStr = self.doxyClass(config)
			else:
				replaceStr = "# " + key + "\n" + pformat(config)


			self.replaceMarkdown(match.start(), match.end(), replaceStr)

		return self.markdown

	def replaceMarkdown(self, start: int, end: int, newString: string):
		self.markdown = self.markdown[:start] + newString + "\n" + self.markdown[end:]

	### Create documentation generator callbacks
	def doxyClass(self, config):
		node = self.finder.doxyClass(config.get("name"), config.get("method"))
		if config.get("method"):
			if not node:
				# return f"**Didnt find methode `{config.get('method')}` in Class `{config.get('name')}`.**"
				return self.generatorBase.error(message=f"Did not find methode `{config.get('method')}` in Class `{config.get('name')}`.")
			md = self.generatorBase.function(node)
		else:
			if not node:
				# return f"**Didn`t find Class `{config.get('name')}`.**`"
				return self.generatorBase.error("Did not find Class", config.get('name'))
			md = self.generatorBase.member(node)
		return md

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


class SnippetClass:
	def __init__(self, config):
		self.config = config

	def default(self):
		return ""