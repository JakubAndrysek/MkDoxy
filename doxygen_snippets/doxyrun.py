from os import path, makedirs
from subprocess import Popen, PIPE, STDOUT
import shlex
import logging

logger = logging.getLogger("mkdocs")


class DoxygenRun:
	"""
	Default config
		INPUT = {self.doxygenSource}
		OUTPUT_DIRECTORY = {self.destinationDir}
		DOXYFILE_ENCODING = UTF-8
		GENERATE_XML = YES
		RECURSIVE = YES
		EXAMPLE_PATH = examples
		SHOW_NAMESPACES = YES
		GENERATE_HTML = NO
		GENERATE_LATEX = NO
	"""
	def __init__(self, doxygenSource, siteDir):
		self.doxygenSource = doxygenSource
		self.destinationDir = path.abspath(path.join(path.join(siteDir, "assets"), "doxy"))

		self.doxyConfig = f"""
		INPUT = {self.doxygenSource}
		OUTPUT_DIRECTORY = {self.destinationDir}
		DOXYFILE_ENCODING = UTF-8
		GENERATE_XML = YES
		RECURSIVE = YES
		EXAMPLE_PATH = examples
		SHOW_NAMESPACES = YES
		GENERATE_HTML = NO
		GENERATE_LATEX = NO
		"""

	def run(self, print_command: bool = False):
		if not path.exists(self.destinationDir):
			makedirs(self.destinationDir)

		doxyBuilder = Popen(['doxygen', '-'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
		stdout_data = doxyBuilder.communicate(self.doxyConfig.encode('utf-8'))[0].decode().strip()
		logger.info(self.destinationDir)
		logger.info(stdout_data)

	def getDestination(self):
		return path.join(self.destinationDir, "xml")
