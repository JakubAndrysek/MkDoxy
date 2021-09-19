import os
import re
import string
import traceback
from typing import TextIO
from jinja2 import Template
from jinja2.exceptions import TemplateSyntaxError, TemplateError
from jinja2 import StrictUndefined, Undefined
from doxygen_snippets.node import Node, DummyNode
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.constants import Kind
from doxygen_snippets.templates.annotated import TEMPLATE as ANNOTATED_TEMPLATE
from doxygen_snippets.templates.member import TEMPLATE as MEMBER_TEMPLATE
from doxygen_snippets.templates.member_definition import TEMPLATE as MEMBER_DEFINITION_TEMPLATE, CONFIG as MEMBER_DEFINITION_CONFIG
from doxygen_snippets.templates.member_table import TEMPLATE as MEMBER_TABLE_TEMPLATE
from doxygen_snippets.templates.namespaces import TEMPLATE as NAMESPACES_TEMPLATE
from doxygen_snippets.templates.classes import TEMPLATE as CLASSES_TEMPLATE
from doxygen_snippets.templates.hierarchy import TEMPLATE as HIEARARCHY_TEMPLATE
from doxygen_snippets.templates.index import TEMPLATE as INDEX_TEMPLATE
from doxygen_snippets.templates.modules import TEMPLATE as MODULES_TEMPLATE
from doxygen_snippets.templates.files import TEMPLATE as FILES_TEMPLATE
from doxygen_snippets.templates.programlisting import TEMPLATE as PROGRAMLISTING_TEMPLATE
from doxygen_snippets.templates.code import TEMPLATE as CODE_TEMPLATE, CONFIG as CODE_CONFIG
from doxygen_snippets.templates.page import TEMPLATE as PAGE_TEMPLATE
from doxygen_snippets.templates.pages import TEMPLATE as PAGES_TEMPLATE
from doxygen_snippets.templates.error import TEMPLATE as ERROR_TEMPLATE

LETTERS = string.ascii_lowercase + '~_@'

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
	def __init__(self, ignore_errors: bool = False, options: dict = {}, debug: bool = False):
		self.options = options
		self.debug = debug

		on_undefined_class = Undefined
		if not ignore_errors:
			on_undefined_class = StrictUndefined

		try:
			self.annotated_template = Template(ANNOTATED_TEMPLATE, undefined=on_undefined_class)
			self.member_template = Template(MEMBER_TEMPLATE, undefined=on_undefined_class)
			self.member_definition_template = Template(MEMBER_DEFINITION_TEMPLATE, undefined=on_undefined_class)
			self.member_table_template = Template(MEMBER_TABLE_TEMPLATE, undefined=on_undefined_class)
			self.namespaces_template = Template(NAMESPACES_TEMPLATE, undefined=on_undefined_class)
			self.classes_template = Template(CLASSES_TEMPLATE, undefined=on_undefined_class)
			self.hiearchy_template = Template(HIEARARCHY_TEMPLATE, undefined=on_undefined_class)
			self.index_template = Template(INDEX_TEMPLATE, undefined=on_undefined_class)
			self.modules_template = Template(MODULES_TEMPLATE, undefined=on_undefined_class)
			self.files_template = Template(FILES_TEMPLATE, undefined=on_undefined_class)
			self.programlisting_template = Template(PROGRAMLISTING_TEMPLATE, undefined=on_undefined_class)
			self.code_template = Template(CODE_TEMPLATE, undefined=on_undefined_class)
			self.page_template = Template(PAGE_TEMPLATE, undefined=on_undefined_class)
			self.pages_template = Template(PAGES_TEMPLATE, undefined=on_undefined_class)
			self.error_template = Template(ERROR_TEMPLATE, undefined=on_undefined_class)
		except TemplateSyntaxError as e:
			raise Exception(str(e) + ' at line: ' + str(e.lineno))

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


	def merge_two_dicts(self, x, y):
		"https://stackoverflow.com/a/26853961"
		z = x.copy()  # start with keys and values of x
		z.update(y)  # modifies z with keys and values of y
		return z

	def error(self, title: str = "", message: str = "", language: str = ""):
		data = {
			'title': title,
			'message': message,
			'language': language,
		}
		return self.render(self.error_template, data)

	def annotated(self, nodes: [Node]):
		data = {
			'nodes': nodes
		}
		return self.render(self.annotated_template, data)

	def programlisting(self, node: [Node], config: dict = {}):
		data = {
			'node': node
		}
		return self.render(self.programlisting_template, data)

	def code(self, node: [Node], config: dict = {}, code: str = ""):
		newConfig = self.merge_two_dicts(CODE_CONFIG, config)

		# if "start" in newConfig:
		# 	code = self.codeStrip(node.programlisting, newConfig.get("start", 1), newConfig.get("end", 0))
		# else:
		# 	code = node.programlisting

		data = {
			'node': node,
			'config': newConfig,
			'code': code
		}

		return self.render(self.code_template, data)

	# def codeStrip(self, codeRaw, start: int = 1, end: int = None):
	# 	regex = r"(?s)````(?P<lang>[a-zA-Z.-_]+)\n(?P<code>.+)````.+"
	# 	matches = re.search(regex, codeRaw, re.MULTILINE)
	# 	lang = matches.group("lang")
	# 	code = matches.group("code")
	#
	# 	print(lang, code)
	#
	# 	lines = code.split("\n")
	# 	out = ""
	#
	# 	if end and start >= end:
	# 		return None
	#
	# 	for num, line in enumerate(lines):
	# 		print(num, line)
	# 		if num >= start and num <= end:
	# 			out += line + "\n"
	# 		elif num >= start and end == 0:
	# 			out += line + "\n"
	#
	# 	return f"```{lang}\n{out}```"

	def fileindex(self, nodes: [Node], config: dict = {}):
		data = {
			'nodes': nodes
		}
		return self.render(self.files_template, data)

	def namespaces(self, nodes: [Node], config: dict = {}):
		data = {
			'nodes': nodes
		}
		return self.render(self.namespaces_template, data)

	def page(self, node: Node):
		data = {
			'node': node
		}
		return self.render(self.page_template, data)

	def relatedpages(self, nodes: [Node], config: dict = {}):
		data = {
			'nodes': nodes
		}
		return self.render(self.pages_template, data)

	def classes(self, nodes: [Node], config: dict = {}):
		classes = self.recursive_find(nodes, Kind.CLASS)
		classes.extend(self.recursive_find(nodes, Kind.STRUCT))
		classes.extend(self.recursive_find(nodes, Kind.INTERFACE))
		dictionary = {}

		for letter in LETTERS:
			dictionary[letter] = []

		for klass in classes:
			dictionary[klass.name_short[0].lower()].append(klass)

		for letter in list(dictionary):
			if len(dictionary[letter]) == 0:
				del dictionary[letter]

		data = {
			'dictionary': dictionary
		}
		return self.render(self.classes_template, data)

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
		return self.render(self.modules_template, data)

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
		return self.render(self.hiearchy_template, data)

	def function(self, node: Node, config: dict = {}):
		newConfig = self.merge_two_dicts(MEMBER_DEFINITION_CONFIG, config)
		data = {
			'node': node,
			'config': newConfig
		}
		return self.render(self.member_definition_template, data)

	def member(self, node: Node, config: dict = {}):
		data = {
			'node': node,
			'member_definition_template': self.member_definition_template,
			'member_table_template': self.member_table_template,
			'config': config
		}
		return self.render(self.member_template, data)

	def file(self, node: Node, config: dict = {}):
		data = {
			'node': node,
			'member_definition_template': self.member_definition_template,
			'member_table_template': self.member_table_template,
			'config': config
		}
		return self.render(self.member_template, data)

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
		return self.render(self.index_template, data)
