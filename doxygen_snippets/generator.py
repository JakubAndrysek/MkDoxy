import os
from typing import Dict
from jinja2 import Template

from lxml import etree
from mkdocs.config import base
from mkdocs.structure import files, pages
import logging

logger = logging.getLogger("mkdocs")


class DocGenerator:
    def __init__(self,
                 markdown,
                 page: pages.Page,
                 config: base.Config,
                 files: files.Files
                 ):
        self.markdown = markdown
        self.page = page
        self.config = config
        self.files = files

    ### Create documentation generator callbacks
    def doxyClass(self,
                  className: str,
                  classMethod: str = None, ):
        return f"## Doxygen CLASS: {className}: {classMethod}"

    def doxyFunction(self, functionName: str):
        return f"## Doxygen FUNCTION: {functionName}"

    ### Create documentation generator callbacks END

    def generateDoc(self):
        mdTemplate = Template(self.markdown)
        # Register documentation generator callbacks
        return mdTemplate.render(doxyClass=self.doxyClass, doxyFunction=self.doxyFunction)
