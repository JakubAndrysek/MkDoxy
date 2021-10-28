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

log = logging.getLogger("mkdocs")

regexLong= r"(?s)(?<!```yaml\n)(^::: doxy\.(?P<project>[a-zA-Z]+)\.(?P<key>[a-zA-Z.-_]+))\s*\n(?P<yaml>.*?)(?:(?:(?:\r*\n)(?=\n))|(?=:::)|`|\Z)" #https://regex101.com/r/lIgOij/2
regexShort = r"(?s)(?<!```yaml\n)(^::: doxy\.(?P<project>[a-zA-Z]+)\.(?P<key>[a-zA-Z.-_]+))\s*\n(?:(?=\n)|(?=:::)|\Z)" # https://regex101.com/r/QnqxRc/1

class GeneratorSnippets:
	def __init__(self,
	             markdown,
	             generatorBase, #: GeneratorBase,
	             doxygen, # Dict[Doxygen],
				 slashPrefix,
	             debug: bool = False):
		self.markdown = markdown
		self.generatorBase = generatorBase
		self.doxygen = doxygen
		self.slashPrefix = slashPrefix
		self.debug = debug
		self.finder = Finder(doxygen, debug)

		self.DOXY_CALL = {
			"code": self.doxyCode,
			"function": self.doxyFunction,
			"class": self.doxyClass,
			"class.method": self.doxyClassMethod,
			"class.list":self.doxyClassList,
			"class.index":self.doxyClassIndex,
			"class.hierarchy":self.doxyClassHierarchy,
			"namespace.list":self.doxyNamespaceList,
			"file.list":self.doxyFileList,
		}

	def generate(self):

		matches = re.finditer(regexShort, self.markdown, re.MULTILINE)
		for match in reversed(list(matches)):
			snippet = match.group()
			key = match.group('key')
			project = match.group('project')

			keyLow = key.lower()
			log.debug(f"\nKey: {keyLow}")

			replaceStr = self.callDoxyByName(snippet, project, keyLow, {})
			self.replaceMarkdown(match.start(), match.end(), replaceStr)

		matches = re.finditer(regexLong, self.markdown, re.MULTILINE)
		for match in reversed(list(matches)):
			if match:
				snippet = match.group()
				key = match.group('key')
				projec = match.group('project')
				keyLow = key.lower()
				log.debug(f"\nKey: {keyLow}")
				yamlRaw = match.group('yaml')
				if yamlRaw:
					try:
						yaml = YAML()
						config = yaml.load(yamlRaw)
						# yaml.dump(config, sys.stdout)
						log.debug(pformat(config))
					except YAMLError as e:
						print(e)

				replaceStr = self.callDoxyByName(snippet, project, keyLow, config)
				self.replaceMarkdown(match.start(), match.end(), replaceStr)


		return self.markdown

	def replaceMarkdown(self, start: int, end: int, newString: string):
		self.markdown = self.markdown[:start] + newString + "\n" + self.markdown[end:]

	def checkProjectExist(self, project: str, snippet):

		return True

	def _recurs_setLinkPrefixNode(self, node: Node, linkPrefix: str):
		node.setLinkPrefix(linkPrefix)
		if node.kind.is_parent():
			self._recurs_setLinkPrefixNodes(node.children, linkPrefix)

	def _recurs_setLinkPrefixNodes(self, nodes: [Node], linkPrefix: str):
		for node in nodes:
			self._recurs_setLinkPrefixNode(node, linkPrefix)

	def callDoxyByName(self, snippet, project: str, key: str, config):
		if key in self.DOXY_CALL:
			funcName = self.DOXY_CALL[key]
			return funcName(snippet, project, config)
		else:
			return self.generatorBase[project].error(f"Did not exist key with name: {key}", snippet, "yaml")

	def checkConfig(self, snippet, project: str, config, params):
		"""
		returns false if config is correct
		return error message if project not exist or find problem in config
		"""
		if not project in self.generatorBase:
			return self.generatorBase[list(self.generatorBase)[0]].error(f"Did not exist project with name: {project}", snippet, "yaml")
		for param in params:
			if not config.get(param):
				return self.doxyError(project, f"The requid parameter `{param}` is not configured!", snippet, "yaml")
		return False

	### Create documentation generator callbacks

	def doxyError(self, project, title: str = "", message: str = "", language: str = ""):
		return self.generatorBase[project].error(title, message, language)
	
	def doxyCode(self, snippet, project: str, config):
		errorMsg = self.checkConfig(snippet, project, config, ["file"])
		if errorMsg:
			return errorMsg
		node = self.finder.doxyCode(project, config.get("file"))
		if isinstance(node, Node):

			progCode = self.codeStrip(node.programlisting, config.get("start", 1), config.get("end", 0))
			if progCode == False:
				return self.doxyError(project, f"Parameter start: {config.get('start')} is greater than end: {config.get('end')}",f"{snippet}", "yaml")
			self._recurs_setLinkPrefixNode(node, self.slashPrefix + project + "/")
			md = self.generatorBase[project].code(node, config, progCode)
			return md
		return self.doxyError(project, f"Did not find File: `{config.get('file')}`", f"{snippet}\nAvailable:\n{pformat(node)}", "yaml")

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


	def doxyFunction(self, snippet, project: str, config):
		errorMsg = self.checkConfig(snippet, project, config, ["name"])
		if errorMsg:
			return errorMsg

		node = self.finder.doxyFunction(project, config.get("name"))
		if isinstance(node, Node):
			self._recurs_setLinkPrefixNode(node, self.slashPrefix + project + "/")
			md = self.generatorBase[project].function(node, config)
			return md
		return self.doxyError(project, f"Did not find Function with name: `{config.get('name')}`", f"{snippet}\nAvailable:\n{pformat(node)}", "yaml")

	def doxyClass(self, snippet, project: str, config):
		errorMsg = self.checkConfig(snippet, project, config, ["name"])
		if errorMsg:
			return errorMsg

		node = self.finder.doxyClass(project, config.get("name"))
		if isinstance(node, Node):
			self._recurs_setLinkPrefixNode(node, self.slashPrefix + project + "/")
			md = self.generatorBase[project].member(node, config)
			return md
		return self.doxyError(project, f"Did not find Class with name: `{config.get('name')}`", f"{snippet}\nAvailable:\n{pformat(node)}", "yaml")

	def doxyClassMethod(self, snippet, project: str, config):
		errorMsg = self.checkConfig(snippet, project, config, ["name", "method"])
		if errorMsg:
			return errorMsg

		node = self.finder.doxyClassMethod(project, config.get("name"), config.get("method"))
		if isinstance(node, Node):
			self._recurs_setLinkPrefixNode(node, self.slashPrefix + project + "/")
			md = self.generatorBase[project].function(node, config)
			return md
		return self.doxyError(project, f"Did not find Class with name: `{config.get('name')}` and method: `{config.get('method')}`", f"{snippet}\nAvailable:\n{pformat(node)}", "yaml")


	def doxyClassList(self, snippet, project: str, config):
		errorMsg = self.checkConfig(snippet, project, config, [])
		if errorMsg:
			return errorMsg
		nodes = self.doxygen[project].root.children
		self._recurs_setLinkPrefixNodes(nodes, self.slashPrefix + project + "/")
		md = self.generatorBase[project].annotated(nodes)
		return md

	def doxyClassIndex(self, snippet, project: str, config):
		errorMsg = self.checkConfig(snippet, project, config, [])
		if errorMsg:
			return errorMsg
		nodes = self.doxygen[project].root.children
		self._recurs_setLinkPrefixNodes(nodes, self.slashPrefix + project + "/")
		md = self.generatorBase[project].classes(nodes)
		return md

	def doxyClassHierarchy(self, snippet, project: str, config):
		errorMsg = self.checkConfig(snippet, project, config, [])
		if errorMsg:
			return errorMsg
		nodes = self.doxygen[project].root.children
		self._recurs_setLinkPrefixNodes(nodes, self.slashPrefix + project + "/")
		md = self.generatorBase[project].hierarchy(nodes)
		return md

	def doxyNamespaceList(self, snippet, project: str, config):
		errorMsg = self.checkConfig(snippet, project, config, [])
		if errorMsg:
			return errorMsg
		nodes = self.doxygen[project].root.children
		self._recurs_setLinkPrefixNodes(nodes, self.slashPrefix + project + "/")
		md = self.generatorBase[project].namespaces(nodes)
		return md

	def doxyFileList(self, snippet, project: str, config):
		errorMsg = self.checkConfig(snippet, project, config, [])
		if errorMsg:
			return errorMsg
		nodes = self.doxygen[project].files.children
		self._recurs_setLinkPrefixNodes(nodes, self.slashPrefix + project + "/")
		md = self.generatorBase[project].fileindex(nodes)
		return md

### Create documentation generator callbacks END


class SnippetClass:
	def __init__(self, config):
		self.config = config

	def default(self):
		return ""