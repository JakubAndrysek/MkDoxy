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

regexLong= r"(?s)(?<!```yaml\n)(^::: doxy.(?P<key>[a-zA-Z.-_]+))\s*\n(?P<yaml>.*?)(?:(?:(?:\r*\n)(?=\n))|(?=:::)|`|\Z)" #https://regex101.com/r/lY9fgm/2
regexShort = r"(?s)(?<!```yaml\n)(^::: doxy.(?P<key>[a-zA-Z.-_]+))\s*\n(?:(?=\n)|(?=:::)|\Z)" #https://regex101.com/r/i3e4g6/1

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

		self.DOXY_CALL = {
			"class": self.doxyClass,
			"class.list":self.doxyClassList,
			"class.index":self.doxyClassIndex,
			"function":self.doxyFunction
		}

	def generate(self):

		matches = re.finditer(regexShort, self.markdown, re.MULTILINE)
		for match in reversed(list(matches)):
			key = match.group('key')

			keyLow = key.lower()
			print(f"Key: {keyLow}")

			replaceStr = self.callDoxyByName(keyLow, {})
			self.replaceMarkdown(match.start(), match.end(), replaceStr)

		matches = re.finditer(regexLong, self.markdown, re.MULTILINE)
		for match in reversed(list(matches)):
			if match:
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

				replaceStr = self.callDoxyByName(keyLow, config)
				self.replaceMarkdown(match.start(), match.end(), replaceStr)


		return self.markdown

	def replaceMarkdown(self, start: int, end: int, newString: string):
		self.markdown = self.markdown[:start] + newString + "\n" + self.markdown[end:]


	def callDoxyByName(self, key, config):
		if key in self.DOXY_CALL:
			funcName = self.DOXY_CALL[key]
			return funcName(config)
		else:
			return self.generatorBase.error(f"Did not exist key with name: {key}")

	def checkConfig(self, config, params):
		"""
		returns false if config is correct
		return error message if find problem in config
		"""
		for param in params:
			if not config.get(param):
				return f"The requid parameter `{param}` is not configured!"
		return False

	def doxyError(self, title: str = "", message: str = ""):
		return self.generatorBase.error(title, message)

	### Create documentation generator callbacks
	def doxyClass(self, config):
		node = self.finder.doxyClass(config.get("name"), config.get("method"))
		if config.get("method"):
			if not node:
				# return f"**Didnt find methode `{config.get('method')}` in Class `{config.get('name')}`.**"
				return self.generatorBase.error(message=f"Did not find method `{config.get('method')}` in Class `{config.get('name')}`.")
			md = self.generatorBase.function(node)
		else:
			if not node:
				# return f"**Didn`t find Class `{config.get('name')}`.**`"
				return self.generatorBase.error("Did not find Class", config.get('name'))
			md = self.generatorBase.member(node)
		return md

	def doxyClassList(self, config):
		md = self.generatorBase.annotated(self.doxygen.root.children)
		return md

	def doxyClassIndex(self, config):
		md = self.generatorBase.classes(self.doxygen.root.children)
		return md

	def doxyClassHierarchy(self, config):
		md = self.generatorBase.hierarchy(self.doxygen.root.children)
		return md

	def doxyFunction(self, config):
		if errorMsg := self.checkConfig(config, ["name"]):
			return self.doxyError(errorMsg)

		function = self.finder.doxyFunction(config.get("name"))
		if function:
			md = self.generatorBase.function(function, config)
			return md
		return self.doxyError(f"Did not find function with name: {config.get('name')}", f"Posible functions: TODO")
		# return f"## Doxygen FUNCTION: {functionName}"

	def doxyNamespaceList(self, config):
		md = self.generatorBase.namespaces(self.doxygen.root.children)
		return md

	def doxyFileList(self, config):
		md = self.generatorBase.fileindex(self.doxygen.files.children)
		return md

### Create documentation generator callbacks END


class SnippetClass:
	def __init__(self, config):
		self.config = config

	def default(self):
		return ""