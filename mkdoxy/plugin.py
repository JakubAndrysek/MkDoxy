"""@package mkdoxy.plugin
MkDoxy → MkDocs + Doxygen = easy documentation generator with code snippets

MkDoxy is a MkDocs plugin for generating documentation from Doxygen XML files.
"""

import logging
from pathlib import Path

from mkdocs.config.base import Config
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from mkdoxy.cache import Cache
from mkdoxy.doxy_config import config_scheme as doxy_config_scheme
from mkdoxy.doxy_config import process_configuration, MkDoxyConfig, MkDoxyConfigProject
from mkdoxy.doxygen import Doxygen
from mkdoxy.doxygen_generator import DoxygenGenerator
from mkdoxy.generator_auto import GeneratorAuto
from mkdoxy.generator_base import GeneratorBase
from mkdoxy.generator_snippets import GeneratorSnippets
from mkdoxy.xml_parser import XmlParser

log: logging.Logger = logging.getLogger("mkdocs")
plugin_name: str = "MkDoxy"


class MkDoxy(BasePlugin):
    """! MkDocs plugin for generating documentation from Doxygen XML files.
    @details
    @param config: (MkDoxyConfig) The global configuration object.
    """

    # Valid configuration options for the plugin
    config_scheme = doxy_config_scheme

    def __init__(self):
        self.doxy_config: MkDoxyConfig = MkDoxyConfig()
        self.generator_base: dict[str, GeneratorBase] = {}
        self.doxygen: dict[str, Doxygen] = {}
        self.mkdocs_config_changed = False
        self.default_template_config = {
            "indent_level": 0,
        }

    def on_config(self, config: Config) -> Config:
        """! Called after the plugin has been initialized.
        @details
        @param config: (Config) The global configuration object.
        @return: (MkDocsConfig) The global configuration object.
        """
        self.doxy_config = process_configuration(self.config)

        log.info(f"Start plugin {plugin_name}")
        if self.config.get("debug", False):
            log.setLevel(logging.DEBUG)
            log.debug("- Debug mode enabled")
        return config

    def on_files(self, files: Files, config: Config) -> Files:
        """! Called after files have been gathered by MkDocs.
        @details generate automatic documentation and append files in the list of files to be processed by mkdocs

        @param files: (Files) The files gathered by MkDocs.
        @param config: (Config) The global configuration object.
        @return: (Files) The files gathered by MkDocs.
        """
        for project_name, project_data in self.doxy_config.projects.items():
            project_data: MkDoxyConfigProject
            log.info(f"-> Processing project '{project_name}'")

            # Generate Doxygen and MD files to user defined folder or default temp folder
            if self.doxy_config.custom_api_folder:
                temp_doxy_folder = Path.joinpath(Path(self.doxy_config.custom_api_folder), Path(project_name))
            else:
                temp_doxy_folder = Path.joinpath(Path(config["site_dir"]), Path("assets/.doxy"), Path(project_name))

            # Create temp dir for Doxygen if not exists
            temp_doxy_folder.mkdir(parents=True, exist_ok=True)

            # Check src changes -> run Doxygen
            doxygen = DoxygenGenerator(
                Path(self.doxy_config.doxygen_bin_path),
                project_data.src_dirs,
                temp_doxy_folder,
                project_data.doxy_config_file,
                project_data.doxy_config_dict,
            )
            if doxygen.has_changes():
                log.info("  -> generating Doxygen files")
                doxygen.run()
                log.info("  -> Doxygen files generated")
            else:
                log.info("  -> skip generating Doxygen files (nothing seems to have changed)")

            # Parse XML to basic structure
            cache = Cache()
            parser = XmlParser(cache=cache, debug=self.doxy_config.debug)

            # Parse basic structure to recursive Nodes
            self.doxygen[project_name] = Doxygen(doxygen.get_output_xml_folder(), parser=parser, cache=cache)

            # Print parsed files
            if self.doxy_config.debug:
                self.doxygen[project_name].print_structure()

            # Prepare generator for future use (GeneratorAuto, SnippetGenerator)
            self.generator_base[project_name] = GeneratorBase(
                project_data.custom_template_dir,
                False,  # ignore_errors=self.config.ignore_errors,
                debug=self.doxy_config.debug,
            )

            if self.doxy_config.full_doc and project_data.full_doc:
                generatorAuto = GeneratorAuto(
                    generator_base=self.generator_base[project_name],
                    temp_doxy_folder=temp_doxy_folder,
                    site_dir=config["site_dir"],
                    api_path=project_name,
                    doxygen=self.doxygen[project_name],
                    use_directory_urls=config["use_directory_urls"],
                )

                project_config = self.default_template_config.copy()
                project_config.update(project_data)

                # Generate full documentation
                generatorAuto.fullDoc(project_config)

                # Generate summary pages
                generatorAuto.summary(project_config)

                # Append files to be processed by MkDocs
                for file in generatorAuto.full_doc_files:
                    files.append(file)
        return files

    def on_page_markdown(self, markdown: str, page: Page, config: Config, files: Files) -> str:
        """! Generate snippets and append them to the markdown.
        @details
        @param markdown: (str) The markdown content of the page.
        @param page: (Page) The page object.
        @param config: (Config) The global configuration object.
        @param files: (Files) The files gathered by MkDocs.
        @return: (str) The markdown content of the page.
        """

        # update default template config with page meta tags
        page_config = self.default_template_config.copy()
        page_config.update(page.meta)

        generator_snippets = GeneratorSnippets(
            markdown=markdown,
            generator_base=self.generator_base,
            doxygen=self.doxygen,
            projects=self.doxy_config.projects,
            use_directory_urls=config.get("use_directory_urls", False),
            page=page,
            config=page_config,
            debug=self.doxy_config.debug,
        )

        return generator_snippets.generate()
