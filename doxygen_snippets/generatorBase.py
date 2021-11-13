import os
import re
import string
import traceback
from dataclasses import dataclass, field
from typing import Tuple
from typing import TextIO
from jinja2.exceptions import TemplateSyntaxError, TemplateError
from jinja2 import StrictUndefined, Undefined
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
import doxygen_snippets
from doxygen_snippets.node import Node, DummyNode
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.constants import Kind
from doxygen_snippets.utils import parseTemplateFile, merge_two_dicts
from mkdocs import exceptions
from markdown import extensions, preprocessors
import logging

log = logging.getLogger("mkdocs")


LETTERS = string.ascii_lowercase + '~_@\\'

ADDITIONAL_FILES = {
	'Namespace List': 'namespaces.md',
	'Namespace Members': 'namespace_members.md',
	'Namespace Member Functions': 'namespace_member_functions.md',
	'Namespace Member Variables': 'namespace_member_variables.md',
	'Namespace Member Typedefs': 'namespace_member_typedefs.md',
	'Namespace Member Enumerations': 'namespace_member_enums.md',
	'Class Index': 'classes.md',
	'Class Hierarchy': 'hierarchy.md',
	'Class Members': 'class_members.md',
	'Class Member Functions': 'class_member_functions.md',
	'Class Member Variables': 'class_member_variables.md',
	'Class Member Typedefs': 'class_member_typedefs.md',
	'Class Member Enumerations': 'class_member_enums.md',
}


def generate_link(name, url) -> str:
	return '* [' + name + '](' + url + ')\n'

class GeneratorBase:
	def __init__(self, ignore_errors: bool = False, debug: bool = False):
		self.options = {} # will be deleted
		self.debug = debug

		on_undefined_class = Undefined
		if not ignore_errors:
			on_undefined_class = StrictUndefined

		self.templates: Dict[str, Template] = {}
		self.metaData: Dict[str, list[str]] = {}

		# code from https://github.com/daizutabi/mkapi/blob/master/mkapi/core/renderer.py#L29-L38
		path = os.path.join(os.path.dirname(doxygen_snippets.__file__), "templates")
		for fileName in os.listdir(path):
			filePath = os.path.join(path, fileName)
			if fileName.endswith(".jinja2"):
				with open(filePath, "r") as file:
					name = os.path.splitext(fileName)[0]
					fileTemplate, metaData = parseTemplateFile(file.read())
					self.templates[name] = Template(fileTemplate)
					self.metaData[name] = metaData
			else:
				log.error(f"Trying to load unsupported file '{filePath}'. Supported file ends with '.jinja2'.")
				
	def loadConfigAndTemplate(self, name: str) -> [Template, dict]:
		template = self.templates.get(name)
		if not template:
			raise exceptions.Abort(f"Trying to load unexisting template '{name}'. Please create a new template file with name '{name}.jinja2'")
		metaData = self.metaData.get(name, {})
		return template, metaData

	def render(self, tmpl: Template, data: dict) -> str:
		try:
			if self.debug:
				print('Generating', path)
			data.update(self.options)
			output = tmpl.render(data)
			return output
		except TemplateError as e:
			raise Exception(str(e))

	def recursive_find(self, nodes: [Node], kind: Kind):
		ret = []
		for node in nodes:
			if node.kind == kind:
				ret.append(node)
			if node.kind.is_parent():
				ret.extend(self.recursive_find(node.children, kind))
		return ret

	def recursive_find_with_parent(self, nodes: [Node], kinds: [Kind], parent_kinds: [Kind]):
		ret = []
		for node in nodes:
			if node.kind in kinds and node.parent is not None and node.parent.kind in parent_kinds:
				ret.append(node)
			if node.kind.is_parent() or node.kind.is_dir() or node.kind.is_file():
				ret.extend(self.recursive_find_with_parent(node.children, kinds, parent_kinds))
		return ret




	def error(self, title: str = "", message: str = "", language: str = ""):
		data = {
			'title': title,
			'message': message,
			'language': language,
		}
		return self.render(self.templates.get("error"), data)

	def annotated(self, nodes: [Node]):
		data = {
			'nodes': nodes
		}
		# return self.render(self.annotated_template, data)
		return self.render(self.templates.get("annotated"), data)

	def programlisting(self, node: [Node], config: dict = {}):
		data = {
			'node': node
		}
		return self.render(self.templates.get("programlisting"), data)

	def code(self, node: [Node], config: dict = {}, code: str = ""):
		newConfig = config
		# newConfig = merge_two_dicts(CODE_CONFIG, config)

		data = {
			'node': node,
			'config': newConfig,
			'code': code
		}

		return self.render(self.templates.get("code"), data)

	def fileindex(self, nodes: [Node], config: dict = {}):
		data = {
			'nodes': nodes
		}
		return self.render(self.templates.get("files"), data)

	def namespaces(self, nodes: [Node], config: dict = {}):
		data = {
			'nodes': nodes
		}
		return self.render(self.templates.get("namespaces"), data)

	def page(self, node: Node):
		data = {
			'node': node
		}
		return self.render(self.templates.get("page"), data)

	def relatedpages(self, nodes: [Node], config: dict = {}):
		data = {
			'nodes': nodes
		}
		return self.render(self.templates.get("page"), data)

	def classes(self, nodes: [Node], config: dict = {}):
		classes = self.recursive_find(nodes, Kind.CLASS)
		classes.extend(self.recursive_find(nodes, Kind.STRUCT))
		classes.extend(self.recursive_find(nodes, Kind.INTERFACE))
		dictionary = {}

		for letter in LETTERS:
			dictionary[letter] = []

		for klass in classes:
			asd = klass.name_short[0].lower()
			dictionary[asd].append(klass)

		for letter in list(dictionary):
			if len(dictionary[letter]) == 0:
				del dictionary[letter]

		data = {
			'dictionary': dictionary
		}
		return self.render(self.templates.get("classes"), data)

	def _find_base_classes(self, nodes: [Node], derived: Node):
		ret = []
		for node in nodes:
			if isinstance(node, str):
				ret.append({
					'refid': node,
					'derived': derived
				})
			elif node.kind.is_parent() and not node.kind.is_namespace():
				bases = node.base_classes
				if len(bases) == 0:
					ret.append(node)
				else:
					ret.extend(self._find_base_classes(bases, node))
		return ret

	def modules(self, nodes: [Node], config: dict = {}):
		data = {
			'nodes': nodes
		}
		return self.render(self.templates.get("modules"), data)

	def hierarchy(self, nodes: [Node], config: dict = {}):
		classes = self.recursive_find(nodes, Kind.CLASS)
		classes.extend(self.recursive_find(nodes, Kind.STRUCT))
		classes.extend(self.recursive_find(nodes, Kind.INTERFACE))

		bases = self._find_base_classes(classes, None)
		deduplicated = {}

		for base in bases:
			if not isinstance(base, dict):
				deduplicated[base.refid] = base

		for base in bases:
			if isinstance(base, dict):
				if base['refid'] not in deduplicated:
					deduplicated[base['refid']] = []
				deduplicated[base['refid']].append(base)

		deduplicated_arr = []
		for key, children in deduplicated.items():
			if isinstance(children, list):
				deduplicated_arr.append(DummyNode(
					key,
					list(map(lambda x: x['derived'], children)),
					Kind.CLASS
				))
			else:
				found: Node = None
				for klass in classes:
					if klass.refid == key:
						found = klass
						break
				if found:
					deduplicated_arr.append(found)

		data = {
			'classes': deduplicated_arr
		}
		return self.render(self.templates.get("hierarchy"), data)

	def function(self, node: Node, config: dict = {}):
		newConfig = config
		# newConfig = merge_two_dicts(MEMBER_DEFINITION_CONFIG, config)
		data = {
			'node': node,
			'config': newConfig
		}
		return self.render(self.templates.get("member_definition"), data)

	def member(self, node: Node, config: dict = {}):
		template, metaConfig = self.loadConfigAndTemplate("member")
		# templateMd, metaConfigMd = self.loadConfigAndTemplate("member_definition")
		# templateMt, metaConfigMt = self.loadConfigAndTemplate("member_table")

		data = {
			'node': node,
			# 'member_definition_template': templateMt,
			# 'member_definition_config': metaConfigMt,
			# 'member_table_template': templateMt,
			'member_definition_template': self.templates.get("member_definition"),
			'member_table_template': self.templates.get("member_table"),
			'config': merge_two_dicts(config, metaConfig)
		}
		return self.render(template, data)
		# return self.render(self.templates.get("member"), data)

	def file(self, node: Node, config: dict = {}):
		data = {
			'node': node,
			'member_definition_template': self.templates.get("member_definition"),
			'member_table_template': self.templates.get("member_table"),
			'config': config
		}
		return self.render(self.templates.get("member"), data)

	def index(self, nodes: [Node], kind_filters: Kind, kind_parents: [Kind], title: str):
		found_nodes = self.recursive_find_with_parent(nodes, kind_filters, kind_parents)
		dictionary = {}

		# Populate initial dictionary
		for letter in LETTERS:
			dictionary[letter] = []

		# Sort items into the dictionary
		for found in found_nodes:
			dictionary[found.name_tokens[-1][0].lower()].append(found)

		# Delete unused letters
		for letter in list(dictionary):
			if len(dictionary[letter]) == 0:
				del dictionary[letter]

		# Sort items if they have the same name
		sorted_dictionary = {}
		for letter, items in dictionary.items():
			d = {}
			for item in items:
				# The name of the item is not yet in the dictionary
				if item.name_short not in d:
					d[item.name_short] = [item.parent]

				# If the key is already in the dictionary,
				# make sure there are no duplicates.
				# For example an overloaded constructor or function!
				# Only allow distinct parents
				else:
					found = False
					for test in d[item.name_short]:
						if test.refid == item.parent.refid:
							found = True
							break
					if not found:
						d[item.name_short].append(item.parent)

			sorted_dictionary[letter] = d

		data = {
			'title': title,
			'dictionary': sorted_dictionary
		}
		return self.render(self.templates.get("index"), data)
