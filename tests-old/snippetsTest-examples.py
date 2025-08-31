from pprint import pprint

from mkdoxy.cache import Cache
from mkdoxy.doxygen import Doxygen
from mkdoxy.xml_parser import XmlParser

if __name__ == "__main__":
    doxygen_source = "src"
    # doxygen_source = "files/src"
    temp_doxy_dir = "temp/doxy"
    site_dir = "temp/doxy"
    api_path = "api"
    target = "mkdocs"
    use_directory_urls = True
    hints = True
    ignore_errors = False
    summary = None
    link_prefix = ""

    # Debug options
    debug = True
    debug_full = False
    full_doc = True

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

    # if debug_full:
    # 	doxygen.print()
    #
    # generatorBase = GeneratorBase(
    #     ignore_errors=ignore_errors, options=options
    # )
    #

    pprint(doxygen)

    # generatorAuto = GeneratorAuto(generatorBase=generatorBase,
    #                               tempDoxyDir=temp_doxy_dir,
    #                               siteDir=site_dir,
    #                               apiPath=api_path,
    #                               useDirectoryUrls=use_directory_urls,
    #                               fullDocFiles=[],
    #                               debug=debug)
    # if fullDoc:
    # 	generatorAuto.fullDoc(doxygen)
    #
    # # find = Finder(doxygen, debug)
    # # fc = find.doxyClass("example::Bird",
    # #                      "Bird (const Bird & other)= delete")
    #
    # generatorSnippets = GeneratorSnippets(
    #     markdown="", generatorBase=generatorBase,
    #     doxygen=doxygen, debug=debug
    # )
    # # func = generatorSnippets.doxyFunction("", {"name":"getRandomNumber()"})
    #
    # # func = generatorSnippets.doxyCode("", {"file":"shape.cppa"})
    # func = generatorSnippets.doxyClassMethod(
    #     "", {"name":"asd", "method":"as"}
    # )
    #
    # pp(func)
