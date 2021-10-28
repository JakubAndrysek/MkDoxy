from os import path, makedirs
from subprocess import Popen, PIPE, STDOUT
import shlex
import logging
from pprint import *

log = logging.getLogger("mkdocs")


class DoxygenRun:
	def __init__(self, doxygenSource: str, tempDoxyFolder: str, doxyCfgNew):
		self.doxygenSource = doxygenSource
		self.tempDoxyFolder = tempDoxyFolder
		self.doxyCfgNew = doxyCfgNew

		self.doxyCfg = {
			"INPUT": self.doxygenSource,
			"OUTPUT_DIRECTORY": self.tempDoxyFolder,
			"DOXYFILE_ENCODING": "UTF-8",
			"GENERATE_XML": "YES",
			"RECURSIVE": "YES",
			"EXAMPLE_PATH": "examples",
			"SHOW_NAMESPACES": "YES",
			"GENERATE_HTML": "NO",
			"GENERATE_LATEX": "NO",
		}

		self.doxyCfg.update(self.doxyCfgNew)
		self.doxyCfgStr = self.dox_dict2str(self.doxyCfg)

	# Source of dox_dict2str: https://xdress-fabio.readthedocs.io/en/latest/_modules/xdress/doxygen.html#XDressPlugin
	def dox_dict2str(self, dox_dict):
		s = ""
		new_line = '{option} = {value}\n'
		for key, value in dox_dict.items():

			if value is True:
				_value = 'YES'
			elif value is False:
				_value = 'NO'
			else:
				_value = value

			s += new_line.format(option=key.upper(), value=_value)

		# Don't need an empty line at the end
		return s.strip()

	def hasChanged(self):
		return True

	def run(self):
		doxyBuilder = Popen(['doxygen', '-'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
		stdout_data = doxyBuilder.communicate(self.doxyCfgStr.encode('utf-8'))[0].decode().strip()
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
