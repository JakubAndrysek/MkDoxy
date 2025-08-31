from pprint import pprint

from doxygen_snippets.cache import Cache
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.doxyrun import DoxygenRun
from doxygen_snippets.generatorAuto import GeneratorAuto
from doxygen_snippets.generatorBase import GeneratorBase
from doxygen_snippets.generatorSnippets import GeneratorSnippets
from doxygen_snippets.xml_parser import XmlParser

if __name__ == "__main__":
    doxygen_source = "files/src-stm32"
    # doxygen_source = "files/src"
    temp_doxy_dir = "files/doxy"
    site_dir = "files/doxy"
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

    doxygen_run = DoxygenRun(doxygen_source, site_dir)
    doxygen_run.run()

    options = {"target": target, "link_prefix": link_prefix}

    cache = Cache()
    parser = XmlParser(cache=cache, target=target, hints=hints, debug=debug)
    doxygen = Doxygen(
        doxygen_run.getDestination(), parser, cache,
        options=options, debug=debug
    )

    if debug_full:
        doxygen.print()

    generator_base = GeneratorBase(
        ignore_errors=ignore_errors, options=options
    )

    generator_auto = GeneratorAuto(
        generatorBase=generator_base,
        tempDoxyDir=temp_doxy_dir,
        siteDir=site_dir,
        apiPath=api_path,
        useDirectoryUrls=use_directory_urls,
        fullDocFiles=[],
        debug=debug,
    )
    if full_doc:
        generator_auto.fullDoc(doxygen)

    # find = Finder(doxygen, debug)
    # fc = find.doxyClass("example::Bird", "Bird (const Bird & other)= delete")

    generator_snippets = GeneratorSnippets(
        markdown="", generatorBase=generator_base,
        doxygen=doxygen, debug=debug
    )
    # func = generatorSnippets.doxyFunction("", {"name":"getRandomNumber()"})

    # func = generatorSnippets.doxyCode("", {"file":"shape.cppa"})
    func = generator_snippets.doxyClassMethod(
        "", {"name": "asd", "method": "as"}
    )

    pprint(func)
