import os
import re
import string
import traceback
from mkdocs.structure import files
from jinja2 import Template
from jinja2.exceptions import TemplateSyntaxError, TemplateError
from jinja2 import StrictUndefined, Undefined
from doxygen_snippets.node import Node, DummyNode
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.constants import Kind
from doxygen_snippets.generatorBase import GeneratorBase


def generate_link(name, url) -> str:
	return '* [' + name + '](' + url + ')\n'


class GeneratorAuto:
	def __init__(self,
	             generatorBase: GeneratorBase,
	             tempDoxyDir: str,
	             siteDir: str,
	             apiPath: str,
				 doxygen: Doxygen,
	             useDirectoryUrls: bool,
	             debug: bool = False):
		self.generatorBase = generatorBase
		self.tempDoxyDir = tempDoxyDir
		self.siteDir = siteDir
		self.apiPath = apiPath
		self.doxygen = doxygen
		self.useDirectoryUrls = useDirectoryUrls,
		self.fullDocFiles = []
		self.debug = debug
		os.makedirs(os.path.join(self.tempDoxyDir, self.apiPath), exist_ok=True)

	def save(self, path: str, output: str):
		pathRel = os.path.join(self.apiPath, path)
		self.fullDocFiles.append(files.File(pathRel, self.tempDoxyDir, self.siteDir, self.useDirectoryUrls))
		with open(os.path.join(self.tempDoxyDir, pathRel), 'w', encoding='utf-8') as file:
			file.write(output)

	def fullDoc(self):
		self.annotated(self.doxygen.root.children)
		self.fileindex(self.doxygen.files.children)
		self.members(self.doxygen.root.children)
		self.members(self.doxygen.groups.children)
		self.files(self.doxygen.files.children)
		self.namespaces(self.doxygen.root.children)
		self.classes(self.doxygen.root.children)
		self.hierarchy(self.doxygen.root.children)
		self.modules(self.doxygen.groups.children)
		self.pages(self.doxygen.pages.children)
		self.relatedpages(self.doxygen.pages.children)
		self.index(self.doxygen.root.children, [Kind.FUNCTION, Kind.VARIABLE, Kind.TYPEDEF, Kind.ENUM],
		           [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE], 'Class Members')
		self.index(self.doxygen.root.children, [Kind.FUNCTION], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
		           'Class Member Functions')
		self.index(self.doxygen.root.children, [Kind.VARIABLE], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
		           'Class Member Variables')
		self.index(self.doxygen.root.children, [Kind.TYPEDEF], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
		           'Class Member Typedefs')
		self.index(self.doxygen.root.children, [Kind.ENUM], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
		           'Class Member Enums')
		self.index(self.doxygen.root.children, [Kind.FUNCTION, Kind.VARIABLE, Kind.TYPEDEF, Kind.ENUM],
		           [Kind.NAMESPACE], 'Namespace Members')
		self.index(self.doxygen.root.children, [Kind.FUNCTION], [Kind.NAMESPACE], 'Namespace Member Functions')
		self.index(self.doxygen.root.children, [Kind.VARIABLE], [Kind.NAMESPACE], 'Namespace Member Variables')
		self.index(self.doxygen.root.children, [Kind.TYPEDEF], [Kind.NAMESPACE], 'Namespace Member Typedefs')
		self.index(self.doxygen.root.children, [Kind.ENUM], [Kind.NAMESPACE], 'Namespace Member Enums')
		self.index(self.doxygen.files.children, [Kind.FUNCTION], [Kind.FILE], 'Functions')
		self.index(self.doxygen.files.children, [Kind.DEFINE], [Kind.FILE], 'Macros')
		self.index(self.doxygen.files.children, [Kind.VARIABLE, Kind.UNION, Kind.TYPEDEF, Kind.ENUM], [Kind.FILE],
		           'Variables')

	def annotated(self, nodes: [Node]):
		path = 'annotated.md'
		output = self.generatorBase.annotated(nodes)
		self.save(path, output)

	def programlisting(self, node: [Node]):
		path = node.refid + '_source.md'

		output = self.generatorBase.programlisting(node)
		self.save(path, output)

	def fileindex(self, nodes: [Node]):
		path = 'files.md'

		output = self.generatorBase.fileindex(nodes)
		self.save(path, output)

	def namespaces(self, nodes: [Node]):
		path = 'namespaces.md'

		output = self.generatorBase.namespaces(nodes)
		self.save(path, output)

	def page(self, node: Node):
		path = node.name + '.md'

		output = self.generatorBase.page(node)
		self.save(path, output)

	def pages(self, nodes: [Node]):
		for node in nodes:
			self.page(node)

	def relatedpages(self, nodes: [Node]):
		path = 'pages.md'

		output = self.generatorBase.annotated(nodes)
		self.save(path, output)

	def classes(self, nodes: [Node]):
		path = 'classes.md'

		output = self.generatorBase.classes(nodes)
		self.save(path, output)

	def modules(self, nodes: [Node]):
		path = 'modules.md'

		output = self.generatorBase.modules(nodes)
		self.save(path, output)

	def hierarchy(self, nodes: [Node]):
		path = 'hierarchy.md'

		output = self.generatorBase.hierarchy(nodes)
		self.save(path, output)

	def member(self, node: Node):
		path = node.filename

		output = self.generatorBase.member(node)
		self.save(path, output)

		if node.is_language or node.is_group or node.is_file or node.is_dir:
			self.members(node.children)

	def file(self, node: Node):
		path = node.filename

		output = self.generatorBase.file(node)
		self.save(path, output)

		if node.is_file and node.has_programlisting:
			self.programlisting(node)

		if node.is_file or node.is_dir:
			self.files(node.children)

	def members(self, nodes: [Node]):
		for node in nodes:
			if node.is_parent or node.is_group or node.is_file or node.is_dir:
				self.member(node)

	def files(self, nodes: [Node]):
		for node in nodes:
			if node.is_file or node.is_dir:
				self.file(node)

	def index(self, nodes: [Node], kind_filters: Kind, kind_parents: [Kind], title: str):
		path = title.lower().replace(' ', '_') + '.md'

		output = self.generatorBase.index(nodes, kind_filters, kind_parents, title)
		self.save(path, output)
