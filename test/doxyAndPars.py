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
	doxyParsers.parseIndex()
	doxyParsers.parseClasses()
	parsedDoxygen = doxyParsers.getParsedDoxygen()

	pprint(parsedDoxygen)

	classCar = GeneratedClassMd(parsedDoxygen, "Car")
	brief = classCar.getBrief()
	detail = classCar.getDetail()

	# pprint(brief.getroottree())
	pprint(classCar.generate())
	# pprint(detail)

	# pprint(brief)

