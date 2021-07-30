from doxygen_snippets.doxygen import *
from doxygen_snippets.parser import *
from doxygen_snippets.generator import *

from beeprint import pp as pprint

if __name__ == '__main__':
	doxygenSource = "cpp_basic/src/"
	doxygenDest = "cpp_basic/doc/"
	doxygen = DoxygenRun(doxygenSource, doxygenDest)
	doxygen.run(print_command=True)

	doxyParsers = DoxygenParser(doxygenDest)
	parsedIndex = doxyParsers.getParsedIndex()
	# pprint(parsedIndex)

	parsedClass = doxyParsers.parseClass("Car")
	if parsedClass:
		pp(parsedClass)
	else:
		print("Class not exist")

	parsedFile = doxyParsers.parseFile("main.cpp")
	if parsedFile:
		pp(parsedFile)
	else:
		print("Not exist")

	parsedXml = doxyParsers.parseXml("std", "namespace")
	if parsedXml:
		pp(parsedXml)
	else:
		print("Not exist")

	pp(doxyParsers.getContent())

