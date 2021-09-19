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
			"code": self.doxyCode,
			"function": self.doxyFunction,
			"class": self.doxyClass,
			"class.method": self.doxyClassMethod,
			"class.list":self.doxyClassList,
			"class.index":self.doxyClassIndex,

		}

	def generate(self):

		matches = re.finditer(regexShort, self.markdown, re.MULTILINE)
		for match in reversed(list(matches)):
			key = match.group('key')

			keyLow = key.lower()
			print(f"\nKey: {keyLow}")

			replaceStr = self.callDoxyByName(snippet, keyLow, {})
			self.replaceMarkdown(match.start(), match.end(), replaceStr)

		matches = re.finditer(regexLong, self.markdown, re.MULTILINE)
		for match in reversed(list(matches)):
			if match:
				snippet = match.group()
				key = match.group('key')
				keyLow = key.lower()
				print(f"\nKey: {keyLow}")
				yamlRaw = match.group('yaml')
				if yamlRaw:
					try:
						yaml = YAML()
						config = yaml.load(yamlRaw)
						yaml.dump(config, sys.stdout)
					except YAMLError as e:
						print(e)

				replaceStr = self.callDoxyByName(snippet, keyLow, config)
				self.replaceMarkdown(match.start(), match.end(), replaceStr)


		return self.markdown

	def replaceMarkdown(self, start: int, end: int, newString: string):
		self.markdown = self.markdown[:start] + newString + "\n" + self.markdown[end:]


	def callDoxyByName(self, snippet, key, config):
		if key in self.DOXY_CALL:
			funcName = self.DOXY_CALL[key]
			return funcName(snippet, config)
		else:
			return self.generatorBase.error(f"Did not exist key with name: {key}")

	def checkConfig(self, snippet, config, params):
		"""
		returns false if config is correct
		return error message if find problem in config
		"""
		for param in params:
			if not config.get(param):
				return self.doxyError(f"The requid parameter `{param}` is not configured!", snippet, "yaml")
		return False

	### Create documentation generator callbacks

	def doxyError(self, title: str = "", message: str = "", language: str = ""):
		return self.generatorBase.error(title, message, language)
	
	def doxyCode(self, snippet, config):
		if errorMsg := self.checkConfig(snippet, config, ["file"]):
			return errorMsg
		node = self.finder.doxyCode(config.get("file"))
		if isinstance(node, Node):

			progCode = self.codeStrip(node.programlisting, config.get("start", 1), config.get("end", 0))
			if progCode == False:
				return self.doxyError(f"Parameter start: {config.get('start')} is greater than end: {config.get('end')}",f"{snippet}", "yaml")

			md = self.generatorBase.code(node, config, progCode)
			return md
		return self.doxyError(f"Did not find File: `{config.get('file')}`", f"{snippet}\nAvailable:\n{pformat(node)}", "yaml")

	def codeStrip(self, codeRaw, start: int = 1, end: int = None):
		regex = r"(?s)````(?P<lang>[a-zA-Z.-_]+)\n(?P<code>.+)````.+"
		matches = re.search(regex, codeRaw, re.MULTILINE)
		lang = matches.group("lang")
		code = matches.group("code")

		# print(lang, code)

		lines = code.split("\n")
		out = ""

		if end and start > end:
			return False

		for num, line in enumerate(lines):
			# print(num, line)
			if num >= start and num <= end:
				out += line + "\n"
			elif num >= start and end == 0:
				out += line + "\n"

		return f"```{lang} linenums='{start}'\n{out}```"


	def doxyFunction(self, snippet, config):
		if errorMsg := self.checkConfig(snippet, config, ["name"]):
			return errorMsg

		node = self.finder.doxyFunction(config.get("name"))
		if isinstance(node, Node):
			md = self.generatorBase.function(node, config)
			return md
		return self.doxyError(f"Did not find Function with name: `{config.get('name')}`", f"{snippet}\nAvailable:\n{pformat(node)}", "yaml")

	def doxyClass(self, snippet, config):
		if errorMsg := self.checkConfig(snippet, config, ["name"]):
			return errorMsg

		node = self.finder.doxyClass(config.get("name"))
		if isinstance(node, Node):
			md = self.generatorBase.member(node, config)
			return md
		return self.doxyError(f"Did not find Class with name: `{config.get('name')}`", f"{snippet}\nAvailable:\n{pformat(node)}", "yaml")

	def doxyClassMethod(self, snippet, config):
		if errorMsg := self.checkConfig(snippet, config, ["name", "method"]):
			return errorMsg

		node = self.finder.doxyClassMethod(config.get("name"), config.get("method"))
		if isinstance(node, Node):
			md = self.generatorBase.function(node, config)
			return md
		return self.doxyError(f"Did not find Class with name: `{config.get('name')}` and method: `{config.get('method')}`", f"{snippet}\nAvailable:\n{pformat(node)}", "yaml")


	def doxyClassList(self, snippet, config):
		md = self.generatorBase.annotated(self.doxygen.root.children)
		return md

	def doxyClassIndex(self, snippet, config):
		md = self.generatorBase.classes(self.doxygen.root.children)
		return md

	def doxyClassHierarchy(self, snippet, config):
		md = self.generatorBase.hierarchy(self.doxygen.root.children)
		return md

	def doxyNamespaceList(self, snippet, config):
		md = self.generatorBase.namespaces(self.doxygen.root.children)
		return md

	def doxyFileList(self, snippet, config):
		md = self.generatorBase.fileindex(self.doxygen.files.children)
		return md

### Create documentation generator callbacks END


class SnippetClass:
	def __init__(self, config):
		self.config = config

	def default(self):
		return ""