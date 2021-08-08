import sys
import os
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.generatorBase import GeneratorBase
from doxygen_snippets.xml_parser import XmlParser
from doxygen_snippets.cache import Cache
from doxygen_snippets.constants import Kind


def run(output: str,
        input: str,
        target: str = 'gitbook',
        hints: bool = True,
        debug: bool = False,
        ignore_errors: bool = False,
        summary: str = None,
        link_prefix: str = ''):
	os.makedirs(output, exist_ok=True)

	options = {
		'target': target,
		'link_prefix': link_prefix
	}

	cache = Cache()
	parser = XmlParser(cache=cache, target=target, hints=hints)
	doxygen = Doxygen(input, parser, cache, options=options)

	if debug:
		doxygen.print()

	generator = GeneratorBase(ignore_errors=ignore_errors, options=options)
	# generator.annotated(output, doxygen.root.children)
	# generator.fileindex(output, doxygen.files.children)
	generator.members(output, doxygen.root.children)
	# generator.members(output, doxygen.groups.children)
	# generator.files(output, doxygen.files.children)
	# generator.namespaces(output, doxygen.root.children)
	# generator.classes(output, doxygen.root.children)
	# generator.hierarchy(output, doxygen.root.children)
	# generator.modules(output, doxygen.groups.children)
	# generator.pages(output, doxygen.pages.children)
	# generator.relatedpages(output, doxygen.pages.children)
	# generator.index(output, doxygen.root.children, [Kind.FUNCTION, Kind.VARIABLE, Kind.TYPEDEF, Kind.ENUM], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE], 'Class Members')
	# generator.index(output, doxygen.root.children, [Kind.FUNCTION], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE], 'Class Member Functions')
	# generator.index(output, doxygen.root.children, [Kind.VARIABLE], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE], 'Class Member Variables')
	# generator.index(output, doxygen.root.children, [Kind.TYPEDEF], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE], 'Class Member Typedefs')
	# generator.index(output, doxygen.root.children, [Kind.ENUM], [Kind.CLASS, Kind.STRUCT, Kind.INTERFACE], 'Class Member Enums')
	# generator.index(output, doxygen.root.children, [Kind.FUNCTION, Kind.VARIABLE, Kind.TYPEDEF, Kind.ENUM], [Kind.NAMESPACE], 'Namespace Members')
	# generator.index(output, doxygen.root.children, [Kind.FUNCTION], [Kind.NAMESPACE], 'Namespace Member Functions')
	# generator.index(output, doxygen.root.children, [Kind.VARIABLE], [Kind.NAMESPACE], 'Namespace Member Variables')
	# generator.index(output, doxygen.root.children, [Kind.TYPEDEF], [Kind.NAMESPACE], 'Namespace Member Typedefs')
	# generator.index(output, doxygen.root.children, [Kind.ENUM], [Kind.NAMESPACE], 'Namespace Member Enums')
	# generator.index(output, doxygen.files.children, [Kind.FUNCTION], [Kind.FILE], 'Functions')
	# generator.index(output, doxygen.files.children, [Kind.DEFINE], [Kind.FILE], 'Macros')
	# generator.index(output, doxygen.files.children, [Kind.VARIABLE, Kind.UNION, Kind.TYPEDEF, Kind.ENUM], [Kind.FILE], 'Variables')

	if target == 'gitbook' and summary:
		generator.summary(output, summary, doxygen.root.children, doxygen.groups.children, doxygen.files.children,
		                  doxygen.pages.children)
