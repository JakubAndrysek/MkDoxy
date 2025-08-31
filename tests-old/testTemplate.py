import os
from pprint import pprint

from doxygen_snippets.cache import Cache
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.doxyrun import DoxygenRun
from doxygen_snippets.generatorAuto import GeneratorAuto
from doxygen_snippets.generatorBase import GeneratorBase
from doxygen_snippets.xml_parser import XmlParser

if __name__ == "__main__":
    doxygen_path = "files/"
    doxygen_input = "src"
    doxygen_output = "doxy"
    doxygen_config = "Doxyfile"
    api_output = "files/docs/"
    target = "mkdocs"
    hints = True
    ignore_errors = False
    summary = None
    link_prefix = ""

    # Debug options
    debug = True
    debug_full = True
    full_doc = True

    os.makedirs(api_output, exist_ok=True)

    doxygen_run = DoxygenRun(
        doxygen_path, doxygen_input, doxygen_output, doxygen_config
    )
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
    generator_auto = GeneratorAuto(generatorBase=generator_base, debug=debug)

    if full_doc:
        generator_auto.fullDoc(api_output, doxygen)

    pprint(generator_auto)
