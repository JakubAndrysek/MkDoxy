import os
from typing import *
from jinja2 import Template

from lxml import etree
from lxml.etree import _Element
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
				 doxyParser: DoxygenParser
				 ):
		self.markdown = markdown
		self.page = page
		self.config = config
		self.files = files
		self.doxyParser = doxyParser

	### Create documentation generator callbacks
	def doxyClass(self,
				  className: str,
				  classMethod: str = None
				  ):
		parsedClass = self.doxyParser.parseClass(className)
		classMd = GeneratedClassMd(parsedClass, className, classMethod)
		# return f"Class:{classMd.generate()}"
		return f"Class:{className}"

	def doxyFunction(self, functionName: str):
		return f"## Doxygen FUNCTION: {functionName}"

	### Create documentation generator callbacks END

	def include(self):
		mdTemplate = Template(self.markdown)
		# Register documentation generator callbacks
		return mdTemplate.render(doxyClass=self.doxyClass, doxyFunction=self.doxyFunction)


class GeneratedClassMd:
	def __init__(self,
	             parsedClass: Union[dict, None],
	             className: str,
	             classMethod: str = None):
		self.parsedClass = parsedClass
		self.className = className
		self.classMethod = classMethod

	def getName(self) -> str:
		return self.className

	def getBrief(self) -> str:
		# print(self.parsedClass["briefdescription"]["para"])
		pprint(self.parsedClass["briefdescription"])
		return ""

	def getDetail(self) -> str:
		# briefXml = self.parsedIndex.classes[self.className]["detaileddescription"]
		# brief = ""
		# for br in briefXml.getchildren():
		# 	brief += br.text
		# return brief
		return ""

	def generate(self):
		# return f"""
		# 	## {self.getName()}
		# 	{self.getBrief()}
		# 	{self.getDetail()}
		# """
		return ""
