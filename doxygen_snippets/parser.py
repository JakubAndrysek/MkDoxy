import os
from typing import Dict
from jinja2 import Template
from typing import Union, List, Dict
from lxml import etree

# import xmltodict
from ssxtd import parsers

from mkdocs.config import base
from mkdocs.structure import files, pages
import logging
from pprint import *

logger = logging.getLogger("mkdocs")


class DoxygenParser:
	def __init__(self, doxygen_path: str):
		self.doxygen_path = doxygen_path

		indexPath = self.getFilePath("index.xml")
		self.parsedIndex = next(parsers.xml_parse(indexPath, depth=0))

	def getParsedIndex(self) -> dict:
		return self.parsedIndex

	def getFilePath(self, filename: str) -> str:
		relative = os.path.join(os.path.join(self.doxygen_path, "xml"), filename)
		index_path = os.path.abspath(relative)
		logger.error(index_path)
		assert os.path.isfile(index_path)
		return index_path

	def getContent(self) -> List[dict]:
		compound = self.parsedIndex["doxygenindex"]["compound"]
		arr = []
		for content in compound:
			arr.append({content["name"]: content["@kind"]})
		return arr

	def getFilename(self, name: str, fileType: str) -> Union[str, None]:
		"""
		:param name:
		:param fileType:
		:return: filename: str or None
		"""
		classes = self.parsedIndex["doxygenindex"]["compound"]
		for doxyClass in classes:
			if doxyClass["name"] == name and doxyClass["@kind"] == fileType:
				return doxyClass["@refid"]
		return None

	def parseXml(self, name: str, xtype: str):
		fileName = self.getFilename(name, xtype)
		if fileName:
			xmlPath = self.getFilePath(f"{fileName}.xml")
			parsedClass = next(parsers.lxml_parse(xmlPath, depth=0, del_empty=False, cleanup_namespaces=False, verbose=True, trim_spaces=False))
			return parsedClass["doxygen"]["compounddef"]
		else:
			return None

	def parseClass(self, className: str) -> Union[dict, None]:
		return self.parseXml(className, "class")

	def parseFile(self, fileName: str) -> Union[dict, None]:
		return self.parseXml(fileName, "file")

	def parseNamespace(self, nsName: str) -> Union[dict, None]:
		return self.parseXml(nsName, "namespace")

	def parseFunction(self, fileName: str, functionName: str) -> Union[dict, None]:
		parsedFile =  self.parseXml(fileName, "file")
		memberdef = parsedFile.get('sectiondef').get('memberdef')
		for function in memberdef:
			if function.get('name') == functionName:
				return function
		return None


