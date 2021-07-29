from mkdocs import utils as mkdocs_utils
from mkdocs.plugins import BasePlugin
from mkdocs.config import base, config_options, Config
from mkdocs.structure import files, pages
from doxygen_snippets.doxygen import DoxygenRun
from doxygen_snippets.parser import DoxygenParser
from doxygen_snippets.generator import DocGenerator
import logging
logger = logging.getLogger("mkdocs")


class DoxygenSnippets(BasePlugin):
    config_scheme = (
        ('doxygen-source', config_options.Type(str, default='')),
        ('doxygen-dest', config_options.Type(str, default='')),
    )

    def __init__(self):
        self.enabled = True
        self.total_time = 0

    def on_pre_build(self, config):
        logger.error("Building Doxygen")
        doxygen_source = self.config["doxygen-source"]
        doxygen_dest = self.config["doxygen-dest"]
        doxygen = DoxygenRun(doxygen_source, doxygen_dest)
        doxygen.run()
        parser = DoxygenParser(doxygen_dest)
        parser.parseIndex()
        logger.error(parser.getParsedXml())
        return

    def on_page_markdown(
            self,
            markdown: str,
            page: pages.Page,
            config: base.Config,
            files: files.Files,
    ) -> str:
        # logger.error("on_page_markdown")
        editMarkdown = DocGenerator(markdown, page, config, files)
        return editMarkdown.generateDoc()

    # def on_serve(self, server):
    #     return server
    #
    # def on_files(self, files: files.Files, config):
    #     return files

    # def on_nav(self, nav, config, files):
    #     return nav
    #
    # def on_env(self, env, config, files):
    #     return env
    #
    # def on_config(self, config):
    #     return config
    #
    # def on_post_build(self, config):
    #     return
    #
    # def on_pre_template(self, template, template_name, config):
    #     return template
    #
    # def on_template_context(self, context, template_name, config):
    #     return context
    #
    # def on_post_template(self, output_content, template_name, config):
    #     return output_content
    #
    # def on_pre_page(self, page: pages.Page, config, files: files.Files):
    #     return page
    #
    # def on_page_read_source(self, page: pages.Page, config):
    #     return
    #
    # def on_page_markdown(self, markdown, page, config, files):
    #     return markdown
    #
    # def on_page_content(self, html, page, config, files):
    #     return html
    #
    # def on_page_context(self, context, page, config, nav):
    #     return context
    #
    # def on_post_page(self, output_content, page, config):
    #     return output_content
