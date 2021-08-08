import argparse
import sys
import os
from doxybook.runner import run

if __name__ == "__main__":
	run(
		input="files/doxy/xml",
		output="files/gen",
		target="mkdocs",
		hints=True,
		debug=True,
		ignore_errors=False,
		summary=None,
		link_prefix=""
	)
