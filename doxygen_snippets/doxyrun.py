from os import path, makedirs
from subprocess import Popen, PIPE, STDOUT
import shlex
import logging

log = logging.getLogger("mkdocs")


class DoxygenRun:
	def __init__(self, doxygenSource, tempDoxyFolder):
		self.doxygenSource = doxygenSource
		self.tempDoxyFolder = tempDoxyFolder

		self.doxyConfig = f"""
		INPUT = {self.doxygenSource}
		OUTPUT_DIRECTORY = {self.tempDoxyFolder}
		DOXYFILE_ENCODING = UTF-8
		GENERATE_XML = YES
		RECURSIVE = YES
		EXAMPLE_PATH = examples
		SHOW_NAMESPACES = YES
		GENERATE_HTML = NO
		GENERATE_LATEX = NO
		"""

	def hasChanged(self):
		return True

	def run(self):
		doxyBuilder = Popen(['doxygen', '-'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
		stdout_data = doxyBuilder.communicate(self.doxyConfig.encode('utf-8'))[0].decode().strip()
		# log.info(self.destinationDir)
		# log.info(stdout_data)

	def checkAndRun(self):
		if self.hasChanged():
			self.run()
			return True
		else:
			return False


	@property
	def path(self):
		return path.join(self.tempDoxyFolder, "xml")
