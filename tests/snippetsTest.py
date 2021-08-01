import argparse
import sys
import os
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.generator import Generator
from doxygen_snippets.xml_parser import XmlParser
from doxygen_snippets.cache import Cache
from doxygen_snippets.constants import Kind
from doxygen_snippets.runner import run
from doxygen_snippets.node import Node
from doxygen_snippets.finder import Finder
from pprint import *

# def findClass(doxygen, className):
#     cache = doxygen.cache.cache
#     for node in cache:
#         if cache[node].name_long == className:
#             return cache[node]
#     return None


if __name__ == "__main__":
    input="/media/kuba/neon/git/robo/rbcx-robotka/RB3204-RBCX-Doc/master/build/RB3204-RBCX-library/doc/xml"
    output="/media/kuba/neon/git/other/web/doxybook/example/mkdocs/docs/api"
    target="mkdocs"
    hints=True
    debug=False
    ignore_errors=False
    summary=None
    link_prefix=""

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

    # pp(doxygen.cache.get('classrb_1_1_angle'))

    find = Finder(doxygen, debug)
    fc = find.doxyClass("rb::Piezo")

    # fc = findClass(doxygen, "rb::Piezo")
    pp(fc)

