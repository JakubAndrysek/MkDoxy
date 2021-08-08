import os
from typing import *
from jinja2 import Template
from mkdocs.config import base
from mkdocs.structure import files, pages
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.finder import Finder

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
		mdTemplate = Template(self.markdown)
		# Register documentation generator callbacks
		return mdTemplate.render(doxyClass=self.doxyClass, doxyFunction=self.doxyFunction)

	### Create documentation generator callbacks
	def doxyClass(self, className: str, methodeName: str = None, *args):
		node = self.finder.doxyClass(className, methodeName)
		if methodeName:
			if not node:
				return f"**Didnt find methode `{methodeName}` in Class `{className}`.**"
			md = self.generatorBase.function(node)
		else:
			if not node:
				return f"**Didn`t find Class `{className}`.**`"
			md = self.generatorBase.member(node)
		return md
		# return f"# Doxygen CLASS {className}-> {fClass.filename}"

	def doxyFunction(self, fileName: str, functionName: str, fullDoc: bool = True):
		# return functionMd.generate()
		return f"## Doxygen FUNCTION: {functionName}"

	### Create documentation generator callbacks END

	# def _render(self, tmpl: Template, data: dict) -> str:
	# 	try:
	# 		data.update(self.options)
	# 		output = tmpl.render(data)
	# 		return output
	# 	except TemplateError as e:
	# 		raise Exception(str(e))
	#
	# def _recursive_find(self, nodes: [Node], kind: Kind):
	# 	ret = []
	# 	for node in nodes:
	# 		if node.kind == kind:
	# 			ret.append(node)
	# 		if node.kind.is_parent():
	# 			ret.extend(self._recursive_find(node.children, kind))
	# 	return ret
	#
	# def _recursive_find_with_parent(self, nodes: [Node], kinds: [Kind], parent_kinds: [Kind]):
	# 	ret = []
	# 	for node in nodes:
	# 		if node.kind in kinds and node.parent is not None and node.parent.kind in parent_kinds:
	# 			ret.append(node)
	# 		if node.kind.is_parent() or node.kind.is_dir() or node.kind.is_file():
	# 			ret.extend(self._recursive_find_with_parent(node.children, kinds, parent_kinds))
	# 	return ret
	#
	# def fullDoc(self, output_dir: str, nodes: Doxygen):
	# 	self.annotated(output_dir, nodes.root.children)
	# 	self.fileindex(output_dir, nodes.files.children)
	# 	self.members(output_dir, nodes.root.children)
	# 	self.members(output_dir, nodes.groups.children)
	# 	self.files(output_dir, nodes.files.children)
	# 	self.namespaces(output_dir, nodes.root.children)
	# 	self.classes(output_dir, nodes.root.children)
	# 	self.hierarchy(output_dir, nodes.root.children)
	# 	self.modules(output_dir, nodes.groups.children)
	# 	self.pages(output_dir, nodes.pages.children)
	# 	self.relatedpages(output_dir, nodes.pages.children)
	# 	self.index(output_dir, nodes.root.children, [Kind.FUNCTION, Kind.VARIABLE, Kind.TYPEDEF, Kind.ENUM],
	# 	           [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE], 'Class Members')
	# 	self.index(output_dir, nodes.root.children, [Kind.FUNCTION], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
	# 	           'Class Member Functions')
	# 	self.index(output_dir, nodes.root.children, [Kind.VARIABLE], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
	# 	           'Class Member Variables')
	# 	self.index(output_dir, nodes.root.children, [Kind.TYPEDEF], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
	# 	           'Class Member Typedefs')
	# 	self.index(output_dir, nodes.root.children, [Kind.ENUM], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE],
	# 	           'Class Member Enums')
	# 	self.index(output_dir, nodes.root.children, [Kind.FUNCTION, Kind.VARIABLE, Kind.TYPEDEF, Kind.ENUM],
	# 	           [Kind.NAMESPACE], 'Namespace Members')
	# 	self.index(output_dir, nodes.root.children, [Kind.FUNCTION], [Kind.NAMESPACE], 'Namespace Member Functions')
	# 	self.index(output_dir, nodes.root.children, [Kind.VARIABLE], [Kind.NAMESPACE], 'Namespace Member Variables')
	# 	self.index(output_dir, nodes.root.children, [Kind.TYPEDEF], [Kind.NAMESPACE], 'Namespace Member Typedefs')
	# 	self.index(output_dir, nodes.root.children, [Kind.ENUM], [Kind.NAMESPACE], 'Namespace Member Enums')
	# 	self.index(output_dir, nodes.files.children, [Kind.FUNCTION], [Kind.FILE], 'Functions')
	# 	self.index(output_dir, nodes.files.children, [Kind.DEFINE], [Kind.FILE], 'Macros')
	# 	self.index(output_dir, nodes.files.children, [Kind.VARIABLE, Kind.UNION, Kind.TYPEDEF, Kind.ENUM], [Kind.FILE],
	# 	           'Variables')
	#
	# def annotated(self, output_dir: str, nodes: [Node]):
	# 	path = os.path.join(output_dir, 'annotated.md')
	#
	# 	data = {
	# 		'nodes': nodes
	# 	}
	# 	self._render(self.annotated_template, path, data)
	#
	# def programlisting(self, output_dir: str, node: [Node]):
	# 	path = os.path.join(output_dir, node.refid + '_source.md')
	#
	# 	data = {
	# 		'node': node
	# 	}
	# 	self._render(self.programlisting_template, path, data)
	#
	# def fileindex(self, output_dir: str, nodes: [Node]):
	# 	path = os.path.join(output_dir, 'files.md')
	#
	# 	data = {
	# 		'nodes': nodes
	# 	}
	# 	self._render(self.files_template, path, data)
	#
	# def namespaces(self, output_dir: str, nodes: [Node]):
	# 	path = os.path.join(output_dir, 'namespaces.md')
	#
	# 	data = {
	# 		'nodes': nodes
	# 	}
	# 	self._render(self.namespaces_template, path, data)
	#
	# def page(self, output_dir: str, node: Node):
	# 	path = os.path.join(output_dir, node.name + '.md')
	#
	# 	data = {
	# 		'node': node
	# 	}
	# 	self._render(self.page_template, path, data)
	#
	# def pages(self, output_dir: str, nodes: [Node]):
	# 	for node in nodes:
	# 		self.page(output_dir, node)
	#
	# def relatedpages(self, output_dir: str, nodes: [Node]):
	# 	path = os.path.join(output_dir, 'pages.md')
	#
	# 	data = {
	# 		'nodes': nodes
	# 	}
	# 	self._render(self.pages_template, path, data)
	#
	# def classes(self, output_dir: str, nodes: [Node]):
	# 	path = os.path.join(output_dir, 'classes.md')
	#
	# 	classes = self._recursive_find(nodes, Kind.CLASS)
	# 	classes.extend(self._recursive_find(nodes, Kind.STRUCT))
	# 	classes.extend(self._recursive_find(nodes, Kind.INTERFACE))
	# 	dictionary = {}
	#
	# 	for letter in LETTERS:
	# 		dictionary[letter] = []
	#
	# 	for klass in classes:
	# 		dictionary[klass.name_short[0].lower()].append(klass)
	#
	# 	for letter in list(dictionary):
	# 		if len(dictionary[letter]) == 0:
	# 			del dictionary[letter]
	#
	# 	data = {
	# 		'dictionary': dictionary
	# 	}
	# 	self._render(self.classes_template, path, data)
	#
	# def _find_base_classes(self, nodes: [Node], derived: Node):
	# 	ret = []
	# 	for node in nodes:
	# 		if isinstance(node, str):
	# 			ret.append({
	# 				'refid': node,
	# 				'derived': derived
	# 			})
	# 		elif node.kind.is_parent() and not node.kind.is_namespace():
	# 			bases = node.base_classes
	# 			if len(bases) == 0:
	# 				ret.append(node)
	# 			else:
	# 				ret.extend(self._find_base_classes(bases, node))
	# 	return ret
	#
	# def modules(self, output_dir: str, nodes: [Node]):
	# 	path = os.path.join(output_dir, 'modules.md')
	#
	# 	data = {
	# 		'nodes': nodes
	# 	}
	# 	self._render(self.modules_template, path, data)
	#
	# def hierarchy(self, output_dir: str, nodes: [Node]):
	# 	path = os.path.join(output_dir, 'hierarchy.md')
	#
	# 	classes = self._recursive_find(nodes, Kind.CLASS)
	# 	classes.extend(self._recursive_find(nodes, Kind.STRUCT))
	# 	classes.extend(self._recursive_find(nodes, Kind.INTERFACE))
	#
	# 	bases = self._find_base_classes(classes, None)
	# 	deduplicated = {}
	#
	# 	for base in bases:
	# 		if not isinstance(base, dict):
	# 			deduplicated[base.refid] = base
	#
	# 	for base in bases:
	# 		if isinstance(base, dict):
	# 			if base['refid'] not in deduplicated:
	# 				deduplicated[base['refid']] = []
	# 			deduplicated[base['refid']].append(base)
	#
	# 	deduplicated_arr = []
	# 	for key, children in deduplicated.items():
	# 		if isinstance(children, list):
	# 			deduplicated_arr.append(DummyNode(
	# 				key,
	# 				list(map(lambda x: x['derived'], children)),
	# 				Kind.CLASS
	# 			))
	# 		else:
	# 			found: Node = None
	# 			for klass in classes:
	# 				if klass.refid == key:
	# 					found = klass
	# 					break
	# 			if found:
	# 				deduplicated_arr.append(found)
	#
	# 	data = {
	# 		'classes': deduplicated_arr
	# 	}
	# 	self._render(self.hiearchy_template, path, data)
	#
	# def member(self, node: Node):
	#
	# 	data = {
	# 		'node': node,
	# 		'member_definition_template': self.member_definition_template,
	# 		'member_table_template': self.member_table_template
	# 	}
	# 	return self._render(self.member_template, data)
	#
	# 	# if node.is_language or node.is_group or node.is_file or node.is_dir:
	# 	# 	self.members(output_dir, node.children)
	#
	# def function(self, node: Node):
	#
	# 	data = {
	# 		'node': node,
	# 	}
	# 	return self._render(self.member_definition_template, data)
	#
	# def file(self, output_dir: str, node: Node):
	# 	path = os.path.join(output_dir, node.filename)
	#
	# 	data = {
	# 		'node': node,
	# 		'member_definition_template': self.member_definition_template,
	# 		'member_table_template': self.member_table_template
	# 	}
	# 	self._render(self.member_template, path, data)
	#
	# 	if node.is_file and node.has_programlisting:
	# 		self.programlisting(output_dir, node)
	#
	# 	if node.is_file or node.is_dir:
	# 		self.files(output_dir, node.children)
	#
	# def members(self, output_dir: str, nodes: [Node]):
	# 	for node in nodes:
	# 		if node.is_parent or node.is_group or node.is_file or node.is_dir:
	# 			self.member(output_dir, node)
	#
	# def files(self, output_dir: str, nodes: [Node]):
	# 	for node in nodes:
	# 		if node.is_file or node.is_dir:
	# 			self.file(output_dir, node)
	#
	# def index(self, output_dir: str, nodes: [Node], kind_filters: Kind, kind_parents: [Kind], title: str):
	# 	path = os.path.join(output_dir, title.lower().replace(' ', '_') + '.md')
	#
	# 	found_nodes = self._recursive_find_with_parent(nodes, kind_filters, kind_parents)
	# 	dictionary = {}
	#
	# 	# Populate initial dictionary
	# 	for letter in LETTERS:
	# 		dictionary[letter] = []
	#
	# 	# Sort items into the dictionary
	# 	for found in found_nodes:
	# 		dictionary[found.name_tokens[-1][0].lower()].append(found)
	#
	# 	# Delete unused letters
	# 	for letter in list(dictionary):
	# 		if len(dictionary[letter]) == 0:
	# 			del dictionary[letter]
	#
	# 	# Sort items if they have the same name
	# 	sorted_dictionary = {}
	# 	for letter, items in dictionary.items():
	# 		d = {}
	# 		for item in items:
	# 			# The name of the item is not yet in the dictionary
	# 			if item.name_short not in d:
	# 				d[item.name_short] = [item.parent]
	#
	# 			# If the key is already in the dictionary,
	# 			# make sure there are no duplicates.
	# 			# For example an overloaded constructor or function!
	# 			# Only allow distinct parents
	# 			else:
	# 				found = False
	# 				for test in d[item.name_short]:
	# 					if test.refid == item.parent.refid:
	# 						found = True
	# 						break
	# 				if not found:
	# 					d[item.name_short].append(item.parent)
	#
	# 		sorted_dictionary[letter] = d
	#
	# 	data = {
	# 		'title': title,
	# 		'dictionary': sorted_dictionary
	# 	}
	# 	self._render(self.index_template, path, data)
	#
	# def _generate_recursive(self, f: TextIO, node: Node, level: int, diff: str):
	# 	if node.kind.is_parent():
	# 		f.write(' ' * level + generate_link(node.kind.value + ' ' + node.name, diff + '/' + node.refid + '.md'))
	# 		for child in node.children:
	# 			self._generate_recursive(f, child, level + 2, diff)
	#
	# def _generate_recursive_files(self, f: TextIO, node: Node, level: int, diff: str):
	# 	if node.kind.is_file() or node.kind.is_dir():
	# 		f.write(' ' * level + generate_link(node.name, diff + '/' + node.refid + '.md'))
	# 		if node.kind.is_file():
	# 			f.write(' ' * level + generate_link(node.name + ' source', diff + '/' + node.refid + '_source.md'))
	# 		for child in node.children:
	# 			self._generate_recursive_files(f, child, level + 2, diff)
	#
	# def _generate_recursive_groups(self, f: TextIO, node: Node, level: int, diff: str):
	# 	if node.kind.is_group():
	# 		f.write(' ' * level + generate_link(node.title, diff + '/' + node.refid + '.md'))
	# 		for child in node.children:
	# 			self._generate_recursive_groups(f, child, level + 2, diff)
	#
	# def _generate_recursive_pages(self, f: TextIO, node: Node, level: int, diff: str):
	# 	if node.kind.is_page():
	# 		f.write(' ' * level + generate_link(node.title, diff + '/' + node.refid + '.md'))
	# 		for child in node.children:
	# 			self._generate_recursive_pages(f, child, level + 2, diff)
	#
	# def summary(self, output_dir: str, summary_file: str, nodes: [Node], modules: [Node], files: [Node], pages: [Node]):
	# 	if self.debug:
	# 		print('Modifying', summary_file)
	# 	summaryDir = os.path.dirname(os.path.abspath(summary_file))
	# 	output_path = os.path.abspath(output_dir)
	# 	diff = output_path[len(summaryDir) + 1:].replace('\\', '/')
	# 	link = diff + '/index.md'
	#
	# 	content = []
	# 	with open(summary_file, 'r') as f:
	# 		content = f.readlines()
	#
	# 	start = None
	# 	offset = 0
	# 	end = None
	# 	for i in range(0, len(content)):
	# 		line = content[i]
	# 		if start is None and re.search(re.escape(link), line):
	# 			m = re.search('\\* \\[', line)
	# 			if m is not None:
	# 				start = m.start()
	# 				start = i
	# 			continue
	#
	# 		if start is not None and end is None:
	# 			if not line.startswith(' ' * (offset + 2)):
	# 				end = i
	#
	# 	if start is None:
	# 		print('WARNING: Could not generate summary! Unable to find \"* [...](' + link + ')\" in SUMMARY.md')
	# 		return
	#
	# 	if end is None:
	# 		end = len(content)
	#
	# 	with open(summary_file, 'w+') as f:
	# 		# Write first part of the file
	# 		for i in range(0, start + 1):
	# 			f.write(content[i])
	#
	# 		f.write(' ' * (offset + 2) + generate_link('Related Pages', diff + '/' + 'pages.md'))
	# 		for node in pages:
	# 			self._generate_recursive_pages(f, node, offset + 4, diff)
	#
	# 		f.write(' ' * (offset + 2) + generate_link('Modules', diff + '/' + 'modules.md'))
	# 		for node in modules:
	# 			self._generate_recursive_groups(f, node, offset + 4, diff)
	#
	# 		f.write(' ' * (offset + 2) + generate_link('Class List', diff + '/' + 'annotated.md'))
	# 		for node in nodes:
	# 			self._generate_recursive(f, node, offset + 4, diff)
	#
	# 		for key, val in ADDITIONAL_FILES.items():
	# 			f.write(' ' * (offset + 2) + generate_link(key, diff + '/' + val))
	#
	# 		f.write(' ' * (offset + 2) + generate_link('Files', diff + '/' + 'files.md'))
	# 		for node in files:
	# 			self._generate_recursive_files(f, node, offset + 4, diff)
	#
	# 		f.write(' ' * (offset + 2) + generate_link('File Variables', diff + '/' + 'variables.md'))
	# 		f.write(' ' * (offset + 2) + generate_link('File Functions', diff + '/' + 'functions.md'))
	# 		f.write(' ' * (offset + 2) + generate_link('File Macros', diff + '/' + 'macros.md'))
	#
	# 		# Write second part of the file
	# 		for i in range(end, len(content)):
	# 			f.write(content[i])
