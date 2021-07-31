
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

	parsedFunction = doxyParsers.parseFunction("main.cpp", "subtract")
	# parsedFunction = doxyParsers.parseFunction("main.cpp", "amIKing")
	if not parsedFunction:
		print("Class name error")

	# pp(parsedFunction)

	subFun = GenerateFunctionMd(parsedFunction)
	test = subFun.generateParam()
	pp(test)
	gen = subFun.generate()
	pp(gen)

	# classCar = GeneratedClassMd(parsedClass, "Car", "setWheelCount")
	# brief = classCar.getBrief()
	# detail = classCar.getDetail()
	# pp(classCar.generate())
	# pp(classCar.getFunction("setWheelCount"))
	# pp(classCar.generate())

	# pprint(brief.getroottree())
	# pprint(classCar.generate())
	# pprint(detail)

	# pprint(brief)

