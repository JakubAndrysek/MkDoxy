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
		('projects', config_options.Type(dict, default='')),
		('full-doc', config_options.Type(bool, default=True)),
		('debug', config_options.Type(bool, default=False)),
		('ignore-errors', config_options.Type(bool, default=False)),
	)

	def on_files(self, files: files.Files, config):
		def tempDir(siteDir: str)->str:
			tempDoxyDir = path.join(siteDir, "assets/.doxy")
			makedirs(tempDoxyDir, exist_ok=True)
			return tempDoxyDir

		self.doxygen = {}
		self.generatorBase = {}
		self.projects = self.config["projects"]
		for projectName in self.projects:

			self.proData = self.projects.get(projectName)
			logger.info(f"Building project {projectName}")

			# Check scr changes -> run Doxygen
			doxygenRun = DoxygenRun(self.proData['src'], tempDir(config['site_dir']))
			if doxygenRun.checkAndRun():
				logger.info("- Running Doxygen")
			else:
				logger.info("- skipping Doxygen")

			cache = Cache()

			self.debug = config.get('debug', False)
			self.options = {
				'link_prefix': "" # relative path in api/
			}

			# Parse XML to bacic structure
			parser = XmlParser(cache=cache, debug=self.debug)

			# Parse bacic structure to recursive Nodes
			self.doxygen[projectName] = Doxygen(doxygenRun.path, parser=parser, cache=cache, options=self.options, debug=self.debug)

			# Print parsed files
			if self.debug:
				logger.warning(pformat(parser))
				self.doxygen[projectName].print()

			# Prepare generator for future use (GeneratorAuto, SnippetGenerator)
			self.generatorBase[projectName] = GeneratorBase(ignore_errors=self.config["ignore-errors"], options=self.options) # options=self.options will be deleted

			if self.config["full-doc"]:
				fullDocFiles = []
				generatorAuto = GeneratorAuto(generatorBase=self.generatorBase[projectName],
											  tempDoxyDir=tempDir(config['site_dir']),
											  siteDir=config['site_dir'],
											  apiPath=projectName,
											  useDirectoryUrls=config['use_directory_urls'],
											  fullDocFiles=fullDocFiles,
											  debug=self.debug)
				generatorAuto.fullDoc(self.doxygen[projectName])
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

		## FIX API Url
		urlSlashCount = page.url.count("/") # count / in url
		if page.url[-1:] == "/":
			urlSlashCount = urlSlashCount - 1 # -1 if ends with / (fold/post/ -> fold/post -> 1 slash)
		slashPrefix = ""
		for i in range(urlSlashCount):
			slashPrefix += "../"
		# for project in self.generatorBase:
			# self.generatorBase[project].options["link_prefix"] = slashPrefix # fix api with ../
		## FIX API Url END

		generatorSnippets = GeneratorSnippets(markdown=markdown, generatorBase=self.generatorBase, doxygen=self.doxygen, slashPrefix = slashPrefix,
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
