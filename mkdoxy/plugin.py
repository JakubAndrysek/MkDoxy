"""@package mkdoxy.plugin
MkDoxy → MkDocs + Doxygen = easy documentation generator with code snippets

MkDoxy is a MkDocs plugin for generating documentation from Doxygen XML files.
"""

import logging
from pathlib import Path


from mkdocs.config import config_options as c
from mkdocs.config.base import Config
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from mkdoxy.cache import Cache
from mkdoxy.doxygen import Doxygen
from mkdoxy.doxygen_generator import DoxygenGenerator
from mkdoxy.generator_auto import GeneratorAuto
from mkdoxy.generator_base import GeneratorBase
from mkdoxy.generator_snippets import GeneratorSnippets
from mkdoxy.xml_parser import XmlParser

log: logging.Logger = logging.getLogger("mkdocs")
plugin_name: str = "MkDoxy"


class MkDoxyConfigProject(Config):
    src_dirs = c.Type(str)  # source directories for Doxygen - INPUT
    full_doc = c.Type(bool, default=True)  # generate full documentation - overwrite global
    debug = c.Type(bool, default=False)  # debug mode - overwrite global
    # ignore_errors = c.Type(bool, default=False)  # ignore errors - overwrite global
    doxy_config_dict = c.Type(dict, default={})  # Doxygen additional configuration - overwrite everything
    doxy_config_file = c.Optional(c.Type(str))  # Doxygen additional configuration
    custom_template_dir = c.Optional(c.Dir())  # custom Jinja2 template directory


class MkDoxyConfig(Config):
    projects = c.DictOfItems(c.SubConfig(MkDoxyConfigProject))  # project configuration - multiple projects
    full_doc = c.Type(bool, default=True)  # generate full documentation - global (all projects)
    debug = c.Type(bool, default=False)  # debug mode
    # ignore_errors = c.Type(bool, default=False)  # ignore errors
    custom_api_folder = c.Optional(c.Type(str))  # custom API folder for Doxygen and MD output (default in temp folder)
    doxygen_bin_path = c.Type(str, default="doxygen")  # path to Doxygen binary - default "doxygen"


class MkDoxy(BasePlugin[MkDoxyConfig]):
    """! MkDocs plugin for generating documentation from Doxygen XML files.
    @details
    @param config: (MkDoxyConfig) The global configuration object.
    """

    def __init__(self):
        self.generator_base: dict[str, GeneratorBase] = {}
        self.doxygen: dict[str, Doxygen] = {}
        self.mkdocs_config_changed = False
        self.default_template_config = {
            "indent_level": 0,
        }

    def on_startup(self, command: str, dirty: bool) -> None:
        pass
        # print("on_startup")
        # mkdocs_config = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        # print(f"mkdocs_config: {mkdocs_config}")
        # raise Exception(f"on_startup {mkdocs_config}")

    def on_config(self, config: MkDoxyConfig) -> MkDoxyConfig:
        """! Called after the plugin has been initialized.
        @details
        @param config: (Config) The global configuration object.
        @return: (MkDocsConfig) The global configuration object.
        """
        log.info(f"Start plugin {plugin_name}")
        if self.config.debug:
            log.setLevel(logging.DEBUG)
            log.debug("- Debug mode enabled")

        # check if config has changed compared to last run
        config_file = self.config.get("config_file_path", None)
        if config_file:
            self.mkdocs_config_changed = self.yaml_config_changes(Path(config_file))
        return config

    def yaml_config_changes(self, config_file, config) -> bool:
        config_file = Path(config_file)
        log.debug(f"- Config file path: {config_file}")

        hash_file_name = ".mkdoxy_hash"

        hash_file_path = (
            Path(self.config.custom_api_folder) / Path(hash_file_name)
            if self.config.custom_api_folder
            else Path(config["site_dir"]) / Path("assets/.doxy") / Path(hash_file_name)
        )
        hash_file_path.parent.mkdir(parents=True, exist_ok=True)

        if hash_file_path.exists():
            log.debug(f"- Hash file exists: {hash_file_path}")
            previous_hash = hash_file_path.read_text()
        else:
            log.debug(f"- Hash file does not exist: {hash_file_path}")
            previous_hash = None

        log.debug(f"- Previous hash: {previous_hash}")

    def on_files(self, files: Files, config: Config) -> Files:
        """! Called after files have been gathered by MkDocs.
        @details generate automatic documentation and append files in the list of files to be processed by mkdocs

        @param files: (Files) The files gathered by MkDocs.
        @param config: (Config) The global configuration object.
        @return: (Files) The files gathered by MkDocs.
        """
        for project_name, project_data in self.config.projects.items():
            project_data: MkDoxyConfigProject
            log.info(f"-> Processing project '{project_name}'")

            # Generate Doxygen and MD files to user defined folder or default temp folder
            if self.config.custom_api_folder:
                temp_doxy_folder = Path.joinpath(Path(self.config.custom_api_folder), Path(project_name))
            else:
                temp_doxy_folder = Path.joinpath(Path(config["site_dir"]), Path("assets/.doxy"), Path(project_name))

            # Create temp dir for Doxygen if not exists
            temp_doxy_folder.mkdir(parents=True, exist_ok=True)

            # Check src changes -> run Doxygen
            doxygen = DoxygenGenerator(
                Path(self.config.doxygen_bin_path),
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
            parser = XmlParser(cache=cache, debug=self.config.debug)

            # Parse basic structure to recursive Nodes
            self.doxygen[project_name] = Doxygen(doxygen.get_output_xml_folder(), parser=parser, cache=cache)

            # Print parsed files
            if self.config.debug:
                self.doxygen[project_name].print_structure()

            # Prepare generator for future use (GeneratorAuto, SnippetGenerator)
            self.generator_base[project_name] = GeneratorBase(
                project_data.custom_template_dir,
                False,  # ignore_errors=self.config.ignore_errors,
                debug=self.config.debug,
            )

            # if self.config["full-doc"] and project_data.get("full-doc", True):
            if self.config.full_doc and project_data.full_doc:
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

        @param markdown (str): The markdown.
        @param page (Page): The MkDocs page.
        @param config (Config): The MkDocs config.
        @param files (Files): The MkDocs files.
        @return: (str) The markdown.
        """

        # update default template config with page meta tags
        page_config = self.default_template_config.copy()
        page_config.update(page.meta)

        generator_snippets = GeneratorSnippets(
            markdown=markdown,
            generator_base=self.generator_base,
            doxygen=self.doxygen,
            projects=self.config.projects,
            use_directory_urls=config.get("use_directory_urls", False),
            page=page,
            config=page_config,
            debug=self.config.debug,
        )

        return generator_snippets.generate()
