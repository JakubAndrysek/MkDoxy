from os import path
import subprocess
import shlex
from doxygen import ConfigParser
from doxygen import Generator

import logging

logger = logging.getLogger("mkdocs")


class DoxygenRun:
	def __init__(self, libPath, sourceDir, destinationDir, doxygenConfig):
		self.libPath = libPath
		self.sourceDir = sourceDir
		self.destinationDir = destinationDir
		self.doxygenConfig = path.abspath(path.join(libPath, doxygenConfig))

		self.config_parser = ConfigParser()
		self.configuration = self.config_parser.load_configuration(self.doxygenConfig)

		self.configuration['INPUT'] = self.sourceDir
		self.configuration['OUTPUT_DIRECTORY'] = self.destinationDir
		self.configuration['DOXYFILE_ENCODING'] = 'UTF-8'
		self.configuration['PROJECT_NAME'] = 'Doxygen snippets'
		self.configuration['GENERATE_HTML'] = 'NO'
		self.configuration['GENERATE_XML'] = 'YES'
		self.configuration['GENERATE_LATEX'] = 'NO'
		self.configuration['XML_OUTPUT'] = 'xml'
		self.configuration['RECURSIVE'] = 'YES'
		self.configuration['FILE_PATTERNS'] = "*.h *.hpp *.md"
		self.configuration['EXAMPLE_PATH'] = 'examples'
		self.configuration['EXAMPLE_PATTERNS'] = '*.cpp'
		self.configuration['SHOW_NAMESPACES'] = 'YES'
		self.configuration['EXTRACT_ALL'] = 'YES'

		# self.configuration['EXCLUDE_PATTERNS'] = '*_deps* *build* *test*'
		# self.configuration['DOXYFILE_ENCODING'] = 'UTF-8'
		# self.configuration['FILE_PATTERNS'] = '*.cpp *.c *.hpp *.h'
		# self.configuration['RECURSIVE'] = 'YES'
		# self.configuration['PROJECT_NAME'] = 'Doxygen snippets'
		# # self.configuration['QUIET'] = 'YES'
		# self.configuration['GENERATE_HTML'] = 'NO'
		# self.configuration['GENERATE_LATEX'] = 'NO'
		# self.configuration['GENERATE_XML'] = 'YES'
		# self.configuration['XML_OUTPUT'] = 'xml'
		# self.configuration['CASE_SENSE_NAMES'] = 'NO'
		# self.configuration['JAVADOC_AUTOBRIEF'] = 'YES'
		# self.configuration['AUTOLINK_SUPPORT'] = 'YES'
		# self.configuration['MACRO_EXPANSION'] = 'YES'
		# self.configuration['EXTRACT_ALL'] = 'YES'
		# self.configuration['FULL_PATH_NAMES'] = 'NO'

		self.configuration['EXAMPLE_PATH'] = 'examples'
		self.configuration['EXAMPLE_PATTERNS'] = '*.cpp'

	def run(self, print_command: bool = False):
		self.config_parser.store_configuration(self.configuration, self.doxygenConfig)
		doxy_builder = Generator(self.doxygenConfig)
		output_zip_archive = doxy_builder.build(clean=False, generate_zip=False)
		return output_zip_archive

	def getDestination(self):
		return path.join(path.join(self.libPath, self.destinationDir), "xml")
