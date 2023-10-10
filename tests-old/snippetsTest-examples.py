from pprint import pprint

from mkdoxy.cache import Cache
from mkdoxy.doxygen import Doxygen
from mkdoxy.xml_parser import XmlParser

if __name__ == "__main__":
    doxygenSource = "src"
    # doxygenSource = "files/src"
    tempDoxyDir = "temp/doxy"
    siteDir = "temp/doxy"
    apiPath = "api"
    target = "mkdocs"
    useDirectoryUrls = True
    hints = True
    ignoreErrors = False
    summary = None
    link_prefix = ""

    # Debug options
    debug = True
    debugFull = False
    fullDoc = True

    # doxygenRun = DoxygenRun(doxygenSource, siteDir, )
    # doxygenRun.run()
    #
    # options = {
    # 	'target': target,
    # 	'link_prefix': link_prefix
    # }

    cache = Cache()
    parser = XmlParser(cache=cache, debug=debug)
    doxygen = Doxygen("data/temp/xml", parser, cache, debug=debug)

    # if debugFull:
    # 	doxygen.print()
    #
    # generatorBase = GeneratorBase(ignore_errors=ignoreErrors, options=options)
    #

    pprint(doxygen)

    # generatorAuto = GeneratorAuto(generatorBase=generatorBase,
    #                               tempDoxyDir=tempDoxyDir,
    #                               siteDir=siteDir,
    #                               apiPath=apiPath,
    #                               useDirectoryUrls=useDirectoryUrls,
    #                               fullDocFiles=[],
    #                               debug=debug)
    # if fullDoc:
    # 	generatorAuto.fullDoc(doxygen)
    #
    # # find = Finder(doxygen, debug)
    # # fc = find.doxyClass("example::Bird", "Bird (const Bird & other)= delete")
    #
    # generatorSnippets = GeneratorSnippets(markdown="", generatorBase=generatorBase, doxygen=doxygen, debug=debug)
    # # func = generatorSnippets.doxyFunction("", {"name":"getRandomNumber()"})
    #
    # # func = generatorSnippets.doxyCode("", {"file":"shape.cppa"})
    # func = generatorSnippets.doxyClassMethod("", {"name":"asd", "method":"as"})
    #
    # pp(func)
