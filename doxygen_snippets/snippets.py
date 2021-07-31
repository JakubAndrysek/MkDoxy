import os
from typing import *
from jinja2 import Template
from mkdocs.config import base
from mkdocs.structure import files, pages
import logging
import re

logger = logging.getLogger("mkdocs")


class IncludeSnippets:
	def __init__(self,
	             markdown,
	             page: pages.Page,
	             config: base.Config,
	             files: files.Files,
	             output_dir: str,
	             nodes: Node
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
		classMd = GenerateClassMd(parsedClass, className, classMethod)
		logger.error(classMethod)
		return classMd.generate()

	# return f"{classMd.generate()}"
	# return f"Class:{className}"

	def doxyFunction(self, fileName: str, functionName: str, fullDoc: bool = True):
		parsedFunc = self.doxyParser.parseFunction(fileName, functionName)
		functionMd = GenerateFunctionMd(parsedFunc, fullDoc)
		return functionMd.generate()
		# return f"## Doxygen FUNCTION: {functionName}"

	### Create documentation generator callbacks END

	def include(self):
		mdTemplate = Template(self.markdown)
		# Register documentation generator callbacks
		return mdTemplate.render(doxyClass=self.doxyClass, doxyFunction=self.doxyFunction)

#
# class GenerateMd:
# 	def getKey(self, param, key: str):
# 		if key in param:
# 			return param.get(key)
# 		else:
# 			return ""
#
# 	def getIndex(self, param, index: int):
# 		if param and index < len(param):
# 			return param[index]
# 		else:
# 			return ""
#
# class GenerateFunctionMd(GenerateMd):
# 	def __init__(self,
# 	             parsedFunction: Union[dict, None],
# 	             fullDoc: bool = True):
# 		self.parsedFunction = parsedFunction
# 		self.functionName = ""
# 		self.fullDoc = fullDoc
#
# 	def test(self):
# 		parameters = {}
# 		# x = self.parsedFunction["detaileddescription"].get("para")[0]
# 		parameterlist = self.parsedFunction["detaileddescription"].get("para")[1]['parameterlist']['#alldata']
# 		for para in parameterlist:
# 			paraName = para['parameteritem']['#alldata'][0]['parameternamelist']["#alldata"][0]['parametername']['#alldata'][0]
# 			paraDesc = para['parameteritem']['#alldata'][1]['parameterdescription']['#alldata'][0]['para']['#alldata'][0]
# 			parameters[paraName] = paraDesc
# 			# pp(x)
# 		# y = self.parsedFunction["detaileddescription"].get("para")[1]['parameterlist']['#alldata'][0]['parameteritem']['#alldata'][0]['parameternamelist']["#alldata"][0]['parametername']['#alldata'][0]
# 		# y2 = self.parsedFunction["detaileddescription"].get("para")[1]['parameterlist']['#alldata'][1]['parameteritem']['#alldata'][0]['parameternamelist']["#alldata"][0]['parametername']['#alldata'][0]
# 		# z = self.parsedFunction["detaileddescription"].get("para")[1]['parameterlist']['#alldata']
# 		return parameters
#
# 	def generateParam(self):
# 		doc = """\
# | Name | Type | Description | Default |
# | ---- | ---- | ----------- | ------- |
# """
# 		if "param" in self.parsedFunction:
# 			param = self.parsedFunction.get("param")
# 			for par in param:
# 				doc += (f"| {self.getKey(param,'type')} | {self.getKey(param,'declname')} | desc | {self.getKey(param,'defval')} |\n")
# 		return doc
#
# 	def generate(self):
# 		doc = f"""\
# # {self.parsedFunction.get("name")}
# {self.getKey(self.getKey(self.parsedFunction, "briefdescription"), "para")}\n
# {self.getIndex(self.getKey(self.getKey(self.parsedFunction, "detaileddescription"), "para"), 0)}
# {self.generateParam()}
# """
# 		# return dedent(doc)
# 		# return re.sub('^\s+', '', doc, flags=re.MULTILINE)
# 		return doc
#
# class GenerateClassMd(GenerateMd):
# 	def __init__(self,
# 	             parsedClass: Union[dict, None],
# 	             className: str,
# 	             classMethod: str = None):
# 		self.parsedClass = parsedClass
# 		self.className = className
# 		self.classMethod = classMethod
#
# 	def getName(self) -> str:
# 		return self.className
#
# 	def getBrief(self) -> str:
# 		if "briefdescription" in self.parsedClass:
# 			return self.parsedClass["briefdescription"]["para"]
# 		else:
# 			return ""
#
# 	def getDetail(self) -> str:
# 		if "detaileddescription" in self.parsedClass:
# 			return self.parsedClass["detaileddescription"]["para"]
# 		else:
# 			return ""
#
# 	def getKind(self, kind: str) -> Union[List[Dict], None]:
# 		ret = []
# 		# pp(self.parsedClass)
# 		if "sectiondef" in self.parsedClass:
# 			sectiondef = self.parsedClass["sectiondef"]
# 			for memberdef in sectiondef:
# 				for method in memberdef["memberdef"]:
# 					if method["@kind"] == kind:
# 						ret.append(method)
# 			return ret
# 		else:
# 			return None
#
# 	def getFunction(self, name):
# 		functions = self.getKind("function")
# 		for function in functions:
# 			# pp(function["name"])
# 			if function["name"] == name:
# 				pp(function)
# 				return f"""
# 					## {function["definition"]}{function["argsstring"]}
# 					{function["briefdescription"]["para"]}
#
# 					Parameters:
# 					| Name | Type | Description | Default |
# 					| ---- |
# 				"""
#
# 	def generate(self):
# 		logger.error(self.getFunction(self.classMethod))
# 		doc = f"""# Class: {self.getName()}
# 					{self.getBrief()}
#
# 					{self.getDetail()}
# 					{self.getFunction(self.classMethod)}
# 		"""
# 		# return re.sub(r"[\n\t\s]*", '', doc)
# 		# return re.sub('\s+', ' ', doc)
# 		return doc.replace('\t', '')
