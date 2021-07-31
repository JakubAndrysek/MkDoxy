import os
from mkdocs import utils as mkdocs_utils
from mkdocs.plugins import BasePlugin
from mkdocs.config import base, config_options, Config
from mkdocs.structure import files, pages

from doxygen_snippets.doxyrun import DoxygenRun
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.generator import Generator
from doxygen_snippets.xml_parser import XmlParser
from doxygen_snippets.cache import Cache
from doxygen_snippets.constants import Kind

import logging
from pprint import *
logger = logging.getLogger("mkdocs")


class DoxygenSnippets(BasePlugin):
	"""
	plugins:
	- search
	- doxygen-snippets:
		doxygen-source:build/RB3204-RBCX-library/src/
		doxygen-dest:build/RB3204-RBCX-library/doc/
		target: mkdocs
		hints: False
		debug: False
		ignore-errors: False
		link_prefix:
	"""

	config_scheme = (
		('doxygen-input', config_options.Type(str, default='')),
		('doxygen-output', config_options.Type(str, default='')),
		('api-output', config_options.Type(str, default='')),
		('target', config_options.Type(str, default='mkdocs')),
		('hints', config_options.Type(bool, default=False)),
		('debug', config_options.Type(bool, default=False)),
		('ignore-errors', config_options.Type(bool, default=False)),
		('link-prefix', config_options.Type(str, default='')),
	)

	def __init__(self):
		self.enabled = True
		self.total_time = 0

	def on_pre_build(self, config):
		# Building Doxygen and parse XML
		logger.error("Building Doxygen and parse XML")
		doxygenInput = self.config["doxygen-input"]
		doxygenOutput = self.config["doxygen-output"]
		apiOutput = self.config["api-output"]
		doxygen = DoxygenRun(doxygenInput, doxygenOutput)
		doxygen.run()
		logger.error(doxygen.getDestination())
		os.makedirs(apiOutput, exist_ok=True)

		options = {
			'target': self.config["target"],
			'link_prefix': self.config["link-prefix"]
		}

		cache = Cache()
		parser = XmlParser(cache=cache, target=self.config['target'], hints=self.config['hints'])
		logger.error(pformat(parser))
		doxygen = Doxygen(doxygen.getDestination(), parser, cache, options=options)

		if self.config["debug"]:
			doxygen.print()

		generator = Generator(ignore_errors=self.config["ignore-errors"], options=options)
		# generator.members(apiOutput, doxygen.root.children)

		generator.annotated(apiOutput, doxygen.root.children)
		generator.fileindex(apiOutput, doxygen.files.children)
		generator.members(apiOutput, doxygen.root.children)
		generator.members(apiOutput, doxygen.groups.children)
		generator.files(apiOutput, doxygen.files.children)
		generator.namespaces(apiOutput, doxygen.root.children)
		generator.classes(apiOutput, doxygen.root.children)
		generator.hierarchy(apiOutput, doxygen.root.children)
		generator.modules(apiOutput, doxygen.groups.children)
		generator.pages(apiOutput, doxygen.pages.children)
		generator.relatedpages(apiOutput, doxygen.pages.children)
		generator.index(apiOutput, doxygen.root.children, [Kind.FUNCTION, Kind.VARIABLE, Kind.TYPEDEF, Kind.ENUM], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE], 'Class Members')
		generator.index(apiOutput, doxygen.root.children, [Kind.FUNCTION], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE], 'Class Member Functions')
		generator.index(apiOutput, doxygen.root.children, [Kind.VARIABLE], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE], 'Class Member Variables')
		generator.index(apiOutput, doxygen.root.children, [Kind.TYPEDEF], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE], 'Class Member Typedefs')
		generator.index(apiOutput, doxygen.root.children, [Kind.ENUM], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE], 'Class Member Enums')
		generator.index(apiOutput, doxygen.root.children, [Kind.FUNCTION, Kind.VARIABLE, Kind.TYPEDEF, Kind.ENUM], [Kind.NAMESPACE], 'Namespace Members')
		generator.index(apiOutput, doxygen.root.children, [Kind.FUNCTION], [Kind.NAMESPACE], 'Namespace Member Functions')
		generator.index(apiOutput, doxygen.root.children, [Kind.VARIABLE], [Kind.NAMESPACE], 'Namespace Member Variables')
		generator.index(apiOutput, doxygen.root.children, [Kind.TYPEDEF], [Kind.NAMESPACE], 'Namespace Member Typedefs')
		generator.index(apiOutput, doxygen.root.children, [Kind.ENUM], [Kind.NAMESPACE], 'Namespace Member Enums')
		generator.index(apiOutput, doxygen.files.children, [Kind.FUNCTION], [Kind.FILE], 'Functions')
		generator.index(apiOutput, doxygen.files.children, [Kind.DEFINE], [Kind.FILE], 'Macros')
		generator.index(apiOutput, doxygen.files.children, [Kind.VARIABLE, Kind.UNION, Kind.TYPEDEF, Kind.ENUM], [Kind.FILE], 'Variables')
		return

	def on_page_markdown(
			self,
			markdown: str,
			page: pages.Page,
			config: base.Config,
			files: files.Files,
	) -> str:
		# Parse markdown and include doxygen snippets
		# logger.error("Parse markdown and include doxygen snippets")
		# editedSnippets = IncludeSnippets(markdown, page, config, files, self.doxyParser)
		# finalMd = editedSnippets.include()
		# logger.error(finalMd)
		# return finalMd
		return markdown

	# def on_serve(self, server):
	#     return server
	#
	# def on_files(self, files: files.Files, config):
	#     return files

	# def on_nav(self, nav, config, files):
	#     return nav
	#
	# def on_env(self, env, config, files):
	#     return env
	#
	# def on_config(self, config):
	#     return config
	#
	# def on_post_build(self, config):
	#     return
	#
	# def on_pre_template(self, template, template_name, config):
	#     return template
	#
	# def on_template_context(self, context, template_name, config):
	#     return context
	#
	# def on_post_template(self, output_content, template_name, config):
	#     return output_content
	#
	# def on_pre_page(self, page: pages.Page, config, files: files.Files):
	#     return page
	#
	# def on_page_read_source(self, page: pages.Page, config):
	#     return
	#
	# def on_page_markdown(self, markdown, page, config, files):
	#     return markdown
	#
	# def on_page_content(self, html, page, config, files):
	#     return html
	#
	# def on_page_context(self, context, page, config, nav):
	#     return context
	#
	# def on_post_page(self, output_content, page, config):
	#     return output_content
