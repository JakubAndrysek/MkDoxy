import os
from mkdocs import utils as mkdocs_utils
from mkdocs.plugins import BasePlugin
from mkdocs.config import base, config_options, Config
from mkdocs.structure import files, pages

from doxygen_snippets.doxyrun import DoxygenRun
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.generatorBase import GeneratorBase
from doxygen_snippets.generatorAuto import GeneratorAuto
from doxygen_snippets.xml_parser import XmlParser
from doxygen_snippets.cache import Cache
from doxygen_snippets.constants import Kind
from doxygen_snippets.snippets import IncludeSnippets
from doxygen_snippets.finder import Finder

import logging
from pprint import *
logger = logging.getLogger("mkdocs")


class DoxygenSnippets(BasePlugin):
	"""
	plugins:
	- search
	- doxygen-snippets
	"""

	config_scheme = (
		('doxygen-path', config_options.Type(str, default='')),
		('doxygen-config', config_options.Type(str, default='')),
		('doxygen-input', config_options.Type(str, default='')),
		('doxygen-output', config_options.Type(str, default='')),
		('api-output', config_options.Type(str, default='')),
		('target', config_options.Type(str, default='mkdocs')),
		('full-doc', config_options.Type(bool, default=False)),
		('hints', config_options.Type(bool, default=False)),
		('debug', config_options.Type(bool, default=False)),
		('full-doc', config_options.Type(bool, default=False)),
		('ignore-errors', config_options.Type(bool, default=False)),
		('link-prefix', config_options.Type(str, default='')),
	)

	def __init__(self):
		self.enabled = True
		self.total_time = 0

	def on_pre_build(self, config):
		# Building Doxygen and parse XML
		logger.warning("Building Doxygen and parse XML")
		self.doxygenPath = self.config["doxygen-path"]
		self.doxygenConfig = self.config["doxygen-config"]
		self.doxygenInput = self.config["doxygen-input"]
		self.doxygenOutput = self.config["doxygen-output"]
		self.apiOutput = self.config["api-output"]
		self.fullDoc = self.config["full-doc"]
		self.ignoreErrors = self.config["ignore-errors"]
		self.target = self.config['target']
		self.hints = self.config['hints']
		self.debug = False

		doxygenRun = DoxygenRun(self.doxygenPath, self.doxygenInput, self.doxygenOutput, self.doxygenConfig)
		doxygenRun.run()

		logger.warning(doxygenRun.getDestination())
		os.makedirs(self.apiOutput, exist_ok=True)

		self.options = {
			'target': self.target,
			'link_prefix': self.config["link-prefix"]
		}

		cache = Cache()
		parser = XmlParser(cache=cache, target=self.target, hints=self.config['hints'], debug=self.debug)
		# logger.warning(pformat(parser))
		self.doxygen = Doxygen(doxygenRun.getDestination(), parser, cache, options=self.options, debug=self.debug)
		logger.warning(pformat(self.doxygen))

		if self.debug:
			self.doxygen.print()

		self.generator = GeneratorBase(ignore_errors=self.ignoreErrors, options=self.options)

		if self.fullDoc:
			generatorAuto = GeneratorAuto(generatorBase=self.generator, debug=self.debug)
			generatorAuto.fullDoc(self.apiOutput, self.doxygen)

		return


	def on_page_markdown(
			self,
			markdown: str,
			page: pages.Page,
			config: base.Config,
			files: files.Files,
	) -> str:
		# Parse markdown and include self.fullDoc snippets
		# logger.warning("Parse markdown and include self.fullDoc snippets")
		options = {
			'target': self.target,
			'link_prefix': "api/"
		}
		editedSnippets = IncludeSnippets(markdown, page, config, files, self.apiOutput, self.doxygen, self.ignoreErrors, options, self.debug)
		finalMd = editedSnippets.include()
		# logger.warning(finalMd)
		return finalMd
		# return markdown

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
