import os
from typing import Dict
from jinja2 import Template

from lxml import etree
from mkdocs.config import base
from mkdocs.structure import files, pages
from doxygen_snippets.parser import *
import logging

logger = logging.getLogger("mkdocs")


class IncludeSnippets:
	def __init__(self,
	             markdown,
	             page: pages.Page,
	             config: base.Config,
	             files: files.Files,
	             parsedDoxygen: DoxygenParser
	             ):
		self.markdown = markdown
		self.page = page
		self.config = config
		self.files = files
		self.parsedDoxygen = parsedDoxygen

	### Create documentation generator callbacks
	def doxyClass(self,
	              className: str,
	              classMethod: str = None, ):
		return f"## Doxygen CLASS: {className}: {classMethod}"

	def doxyFunction(self, functionName: str):
		return f"## Doxygen FUNCTION: {functionName}"

	### Create documentation generator callbacks END

	def include(self):
		mdTemplate = Template(self.markdown)
		# Register documentation generator callbacks
		return mdTemplate.render(doxyClass=self.doxyClass, doxyFunction=self.doxyFunction)


class GeneratedClassMd:
	def __init__(self,
	             parsedDoxygen: DoxygenParser,
	             className: str,
	             classMethod: str = None) :
		self.parsedDoxygen = parsedDoxygen
		self.className = className
		self.classMethod = classMethod

	def generateBrief(self):
		return self.parsedDoxygen["class"][self.className]["briefdescription"]
