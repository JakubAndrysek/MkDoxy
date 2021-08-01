import argparse
import sys
import os
from doxybook.runner import run

if __name__ == "__main__":
    run(
        input="/media/kuba/neon/git/robo/rbcx-robotka/RB3204-RBCX-Doc/master/build/RB3204-RBCX-library/doc/xml",
        output="/media/kuba/neon/git/other/web/doxybook/example/mkdocs/docs/api",
        target="mkdocs",
        hints=True,
        debug=False,
        ignore_errors=False,
        summary=None,
        link_prefix=""
    )