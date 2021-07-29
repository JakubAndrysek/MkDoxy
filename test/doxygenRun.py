from doxygen_snippets.doxygen import DoxygenRun

if __name__ == '__main__':
	doxygen = DoxygenRun("cpp_basic/src/", "cpp_basic/doc/")
	doxygen.run(print_command=True)