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
	def __init__(self, generatorBase: GeneratorBase, config, fullDocFiles: dict = [], debug: bool = False):
		self.generatorBase = generatorBase
		self.config = config
		self.fullDocFiles = fullDocFiles
		self.debug = debug

	def save(self, path: str, output: str):
		# print(f"File: {path}, '/tmp/asd/', {self.config['site_dir']}")
		self.fullDocFiles.append(files.File(path, self.config['docs_dir'], self.config['site_dir'], self.config['use_directory_urls']))
		with open(path, 'w', encoding='utf-8') as file:
			file.write(output)

	def fullDoc(self, output_dir: str, nodes: Doxygen):
		os.makedirs(output_dir, exist_ok=True)

		self.annotated(output_dir, nodes.root.children)
		self.fileindex(output_dir, nodes.files.children)
		self.members(output_dir, nodes.root.children)
		self.members(output_dir, nodes.groups.children)
		self.files(output_dir, nodes.files.children)
		self.namespaces(output_dir, nodes.root.children)
		self.classes(output_dir, nodes.root.children)
		self.hierarchy(output_dir, nodes.root.children)
		self.modules(output_dir, nodes.groups.children)
		self.pages(output_dir, nodes.pages.children)
		self.relatedpages(output_dir, nodes.pages.children)
		self.index(output_dir, nodes.root.children, [Kind.FUNCTION, Kind.VARIABLE, Kind.TYPEDEF, Kind.ENUM],
		           [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE], 'Class Members')
		self.index(output_dir, nodes.root.children, [Kind.FUNCTION], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
		           'Class Member Functions')
		self.index(output_dir, nodes.root.children, [Kind.VARIABLE], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
		           'Class Member Variables')
		self.index(output_dir, nodes.root.children, [Kind.TYPEDEF], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
		           'Class Member Typedefs')
		self.index(output_dir, nodes.root.children, [Kind.ENUM], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
		           'Class Member Enums')
		self.index(output_dir, nodes.root.children, [Kind.FUNCTION, Kind.VARIABLE, Kind.TYPEDEF, Kind.ENUM],
		           [Kind.NAMESPACE], 'Namespace Members')
		self.index(output_dir, nodes.root.children, [Kind.FUNCTION], [Kind.NAMESPACE], 'Namespace Member Functions')
		self.index(output_dir, nodes.root.children, [Kind.VARIABLE], [Kind.NAMESPACE], 'Namespace Member Variables')
		self.index(output_dir, nodes.root.children, [Kind.TYPEDEF], [Kind.NAMESPACE], 'Namespace Member Typedefs')
		self.index(output_dir, nodes.root.children, [Kind.ENUM], [Kind.NAMESPACE], 'Namespace Member Enums')
		self.index(output_dir, nodes.files.children, [Kind.FUNCTION], [Kind.FILE], 'Functions')
		self.index(output_dir, nodes.files.children, [Kind.DEFINE], [Kind.FILE], 'Macros')
		self.index(output_dir, nodes.files.children, [Kind.VARIABLE, Kind.UNION, Kind.TYPEDEF, Kind.ENUM], [Kind.FILE],
		           'Variables')

	def annotated(self, output_dir: str, nodes: [Node]):
		path = os.path.join(output_dir, 'annotated.md')

		output = self.generatorBase.annotated(nodes)
		self.save(path, output)

	def programlisting(self, output_dir: str, node: [Node]):
		path = os.path.join(output_dir, node.refid + '_source.md')

		output = self.generatorBase.programlisting(node)
		self.save(path, output)

	def fileindex(self, output_dir: str, nodes: [Node]):
		path = os.path.join(output_dir, 'files.md')

		output = self.generatorBase.fileindex(nodes)
		self.save(path, output)

	def namespaces(self, output_dir: str, nodes: [Node]):
		path = os.path.join(output_dir, 'namespaces.md')

		output = self.generatorBase.namespaces(nodes)
		self.save(path, output)

	def page(self, output_dir: str, node: Node):
		path = os.path.join(output_dir, node.name + '.md')

		output = self.generatorBase.page(node)
		self.save(path, output)

	def pages(self, output_dir: str, nodes: [Node]):
		for node in nodes:
			self.page(output_dir, node)

	def relatedpages(self, output_dir: str, nodes: [Node]):
		path = os.path.join(output_dir, 'pages.md')

		output = self.generatorBase.annotated(nodes)
		self.save(path, output)

	def classes(self, output_dir: str, nodes: [Node]):
		path = os.path.join(output_dir, 'classes.md')

		output = self.generatorBase.classes(nodes)
		self.save(path, output)

	def modules(self, output_dir: str, nodes: [Node]):
		path = os.path.join(output_dir, 'modules.md')

		output = self.generatorBase.modules(nodes)
		self.save(path, output)

	def hierarchy(self, output_dir: str, nodes: [Node]):
		path = os.path.join(output_dir, 'hierarchy.md')

		output = self.generatorBase.hierarchy(nodes)
		self.save(path, output)

	def member(self, output_dir: str, node: Node):
		path = os.path.join(output_dir, node.filename)

		output = self.generatorBase.member(node)
		self.save(path, output)

		if node.is_language or node.is_group or node.is_file or node.is_dir:
			self.members(output_dir, node.children)

	def file(self, output_dir: str, node: Node):
		path = os.path.join(output_dir, node.filename)

		output = self.generatorBase.file(node)
		self.save(path, output)

		if node.is_file and node.has_programlisting:
			self.programlisting(output_dir, node)

		if node.is_file or node.is_dir:
			self.files(output_dir, node.children)

	def members(self, output_dir: str, nodes: [Node]):
		for node in nodes:
			if node.is_parent or node.is_group or node.is_file or node.is_dir:
				self.member(output_dir, node)

	def files(self, output_dir: str, nodes: [Node]):
		for node in nodes:
			if node.is_file or node.is_dir:
				self.file(output_dir, node)

	def index(self, output_dir: str, nodes: [Node], kind_filters: Kind, kind_parents: [Kind], title: str):
		path = os.path.join(output_dir, title.lower().replace(' ', '_') + '.md')

		output = self.generatorBase.index(nodes, kind_filters, kind_parents, title)
		self.save(path, output)
