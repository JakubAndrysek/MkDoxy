from os import path, makedirs
from mkdocs import utils as mkdocs_utils
from mkdocs.plugins import BasePlugin
from mkdocs.config import base, config_options, Config
from mkdocs.structure import files, pages
from mkdocs.commands import serve

from doxygen_snippets.doxyrun import DoxygenRun
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.generatorBase import GeneratorBase
from doxygen_snippets.generatorAuto import GeneratorAuto
from doxygen_snippets.xml_parser import XmlParser
from doxygen_snippets.cache import Cache
from doxygen_snippets.constants import Kind
from doxygen_snippets.generatorSnippets import GeneratorSnippets
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
		('doxygen-source', config_options.Type(str, default='')),
		('api-path', config_options.Type(str, default='api')),
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

	# def on_serve(self, server, config, **kwargs):
	# # def on_serve(self, server: serve.LiveReloadServer, config, **kwargs):
	# 	logger.error("Run on serve")
	# 	logger.error(self.config)
	# 	return server

	def on_files(self, files: files.Files, config):
		# Building Doxygen and parse XML
		logger.warning("Building Doxygen and parse XML")
		self.doxygenSource = self.config["doxygen-source"]
		self.apiPath = self.config["api-path"]
		self.fullDoc = self.config["full-doc"]
		self.ignoreErrors = self.config["ignore-errors"]
		self.target = self.config['target']
		self.hints = self.config['hints']
		self.useDirectoryUrls = config['use_directory_urls']
		self.debug = False

		self.siteDir = config['site_dir']
		self.tempDoxyDir = path.join(self.siteDir, "assets/.doxy")
		makedirs(self.tempDoxyDir, exist_ok=True)

		doxygenRun = DoxygenRun(self.doxygenSource, self.tempDoxyDir)
		doxygenRun.run()

		# logger.warning(pformat(config))
		# logger.warning(doxygenRun.getDestination())

		self.options = {
			'target': self.target,
			'link_prefix': self.config["link-prefix"]
		}

		cache = Cache()
		parser = XmlParser(cache=cache, target=self.target, hints=self.config['hints'], debug=self.debug)
		self.doxygen = Doxygen(doxygenRun.getDestination(), parser, cache, options=self.options, debug=self.debug)
		logger.warning(pformat(self.doxygen))

		if self.debug:
			logger.warning(pformat(parser))
			self.doxygen.print()

		self.generatorBase = GeneratorBase(ignore_errors=self.ignoreErrors, options=self.options)

		if self.fullDoc:
			self.fullDocFiles = []
			generatorAuto = GeneratorAuto(generatorBase=self.generatorBase,
			                              tempDoxyDir=self.tempDoxyDir,
			                              siteDir=self.siteDir,
			                              apiPath=self.apiPath,
			                              useDirectoryUrls=self.useDirectoryUrls,
			                              fullDocFiles=self.fullDocFiles,
			                              debug=self.debug)
			generatorAuto.fullDoc(self.doxygen)
			for file in generatorAuto.fullDocFiles:
				files.append(file)

		return files

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
			'link_prefix': self.apiPath+"/"
		}
		generatorSnippets = GeneratorSnippets(markdown=markdown, generatorBase=self.generatorBase, doxygen=self.doxygen,
		                                      debug=self.debug)
		finalMd = generatorSnippets.generate()
		# logger.warning(finalMd)
		return finalMd
	# return markdown

# def on_pre_build(self, config):

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
