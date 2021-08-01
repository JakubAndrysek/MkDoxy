import os
import re
import string
import traceback
from typing import TextIO
from jinja2 import Template
from jinja2.exceptions import TemplateSyntaxError, TemplateError
from jinja2 import StrictUndefined, Undefined
from doxygen_snippets.node import Node, DummyNode
from doxygen_snippets.doxygen import Doxygen
from doxygen_snippets.constants import Kind

class Finder:
	def __init__(self, doxygen, debug: bool = False):
		self.doxygen = doxygen
		self.debug = debug

	def doxyClass(self, className):
		cache = self.doxygen.cache.cache
		for node in cache:
			if cache[node].name_long == className:
				return cache[node]
		return None


