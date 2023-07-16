import hashlib
import logging
import tempfile
from pathlib import Path, PurePath
from subprocess import Popen, PIPE
from typing import Optional

log: logging.Logger = logging.getLogger("mkdocs")


class DoxygenRun:
	"""! Class for running Doxygen.
	@details This class is used to run Doxygen and parse the XML output.
	"""
	def __init__(self, doxygenBinPath: str, doxygenSource: str, tempDoxyFolder: str, doxyCfgNew, runPath: Optional[str] = None):
		"""! Constructor.
		Default Doxygen config options:

		- INPUT: <doxygenSource>
		- OUTPUT_DIRECTORY: <tempDoxyFolder>
		- DOXYFILE_ENCODING: UTF-8
		- GENERATE_XML: YES
		- RECURSIVE: YES
		- EXAMPLE_PATH: examples
		- SHOW_NAMESPACES: YES
		- GENERATE_HTML: NO
		- GENERATE_LATEX: NO

		@details
		@param doxygenBinPath: (str) Path to the Doxygen binary.
		@param doxygenSource: (str) Source files for Doxygen.
		@param tempDoxyFolder: (str) Temporary folder for Doxygen.
		@param doxyCfgNew: (dict) New Doxygen config options that will be added to the default config (new options will overwrite default options)
		"""
		self.doxygenBinPath: str = doxygenBinPath
		self.doxygenSource: str = doxygenSource
		self.tempDoxyFolder: str = tempDoxyFolder
		self.doxyCfgNew: dict = doxyCfgNew
		self.hashFileName: str = "hashChanges.yaml"
		self.hashFilePath: PurePath = PurePath.joinpath(Path(self.tempDoxyFolder), Path(self.hashFileName))
		self.runPath: Optional[str] = runPath

		self.doxyCfg: dict = {
			"INPUT": self.doxygenSource,
			"OUTPUT_DIRECTORY": self.tempDoxyFolder,
			"DOXYFILE_ENCODING": "UTF-8",
			"GENERATE_XML": "YES",
			"RECURSIVE": "YES",
			"SHOW_NAMESPACES": "YES",
			"GENERATE_HTML": "NO",
			"GENERATE_LATEX": "NO",
		}

		self.doxyCfg.update(self.doxyCfgNew)
		self.doxyCfgStr: str = self.dox_dict2str(self.doxyCfg)

	# Source of dox_dict2str: https://xdress-fabio.readthedocs.io/en/latest/_modules/xdress/doxygen.html#XDressPlugin
	def dox_dict2str(self, dox_dict: dict) -> str:
		"""! Convert a dictionary to a string that can be written to a doxygen config file.
		@details
		@param dox_dict: (dict) Dictionary to convert.
		@return: (str) String that can be written to a doxygen config file.
		"""
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
		"""! Check if the source files have changed since the last run.
		@details
		@return: (bool) True if the source files have changed since the last run.
		"""
		def heshWrite(filename: str, hash: str):
			with open(filename, "w") as file:
				file.write(hash)

		def hashRead(filename: str) -> str:
			with open(filename, "r") as file:
				return str(file.read())

		sha1 = hashlib.sha1()
		srcs = self.doxygenSource.split(" ")
		for src in srcs:
			for path in Path(src).rglob('*.*'):
				# # Code from https://stackoverflow.com/a/22058673/15411117
				# # BUF_SIZE is totally arbitrary, change for your app!
				BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
				if path.is_file():
					with open(path, 'rb') as f:
						while True:
							data = f.read(BUF_SIZE)
							if not data:
								break
							sha1.update(data)
				# print(f"{path}: {sha1.hexdigest()}")

		hahsNew = sha1.hexdigest()
		if Path(self.hashFilePath).is_file():
			hashOld = hashRead(self.hashFilePath)
			if hahsNew == hashOld:
				return False

		heshWrite(self.hashFilePath, hahsNew)
		return True

	def run(self):
		"""! Run Doxygen with the current configuration using the Popen class.
		@details
		"""
		doxyBuilder = Popen([self.doxygenBinPath, '-'], stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd=self.runPath)
		stdout_data = doxyBuilder.communicate(self.doxyCfgStr.encode('utf-8'))[0].decode().strip()
		# log.info(self.destinationDir)
		# log.info(stdout_data)

	def checkAndRun(self):
		"""! Check if the source files have changed since the last run and run Doxygen if they have.
		@details
		@return: (bool) True if Doxygen was run.
		"""
		if self.hasChanged():
			self.run()
			return True
		else:
			return False


	def getOutputFolder(self) -> PurePath:
		"""! Get the path to the XML output folder.
		@details
		@return: (PurePath) Path to the XML output folder.
		"""
		return Path.joinpath(Path(self.tempDoxyFolder), Path("xml"))
