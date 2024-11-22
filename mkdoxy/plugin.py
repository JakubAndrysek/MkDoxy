"""@package mkdoxy.plugin
MkDoxy → MkDocs + Doxygen = easy documentation generator with code snippets

MkDoxy is a MkDocs plugin for generating documentation from Doxygen XML files.
"""

import logging
from pathlib import Path, PurePath

from mkdocs import exceptions
from mkdocs.config import Config, base, config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure import files, pages

from mkdoxy.cache import Cache
from mkdoxy.doxygen import Doxygen
from mkdoxy.doxyrun import DoxygenRun
from mkdoxy.generatorAuto import GeneratorAuto
from mkdoxy.generatorBase import GeneratorBase
from mkdoxy.generatorSnippets import GeneratorSnippets
from mkdoxy.xml_parser import XmlParser

log: logging.Logger = logging.getLogger("mkdocs")
pluginName: str = "MkDoxy"


class MkDoxy(BasePlugin):
    """! MkDocs plugin for generating documentation from Doxygen XML files."""

    # Config options for the plugin
    config_scheme = (
        ("projects", config_options.Type(dict, default={})),
        ("full-doc", config_options.Type(bool, default=True)),
        ("debug", config_options.Type(bool, default=False)),
        ("ignore-errors", config_options.Type(bool, default=False)),
        ("save-api", config_options.Type(str, default="")),
        ("enabled", config_options.Type(bool, default=True)),
        (
            "doxygen-bin-path",
            config_options.Type(str, default="doxygen", required=False),
        ),
    )

    # Config options for each project
    config_project = (
        ("src-dirs", config_options.Type(str)),
        ("full-doc", config_options.Type(bool, default=True)),
        ("debug", config_options.Type(bool, default=False)),
        # ('ignore-errors', config_options.Type(bool, default=False)),
        ("api-path", config_options.Type(str, default=".")),
        ("doxy-cfg", config_options.Type(dict, default={}, required=False)),
        ("doxy-cfg-file", config_options.Type(str, default="", required=False)),
        ("template-dir", config_options.Type(str, default="", required=False)),
    )

    def is_enabled(self) -> bool:
        """! Checks if the plugin is enabled
        @details
        @return: (bool) True if the plugin is enabled.
        """
        return self.config.get("enabled")

    def on_files(self, files: files.Files, config: base.Config) -> files.Files:
        """! Called after files have been gathered by MkDocs.
        @details

        @param files: (Files) The files gathered by MkDocs.
        @param config: (Config) The global configuration object.
        @return: (Files) The files gathered by MkDocs.
        """
        if not self.is_enabled():
            return files

        def checkConfig(config_project, proData, strict: bool):
            cfg = Config(config_project, "")
            cfg.load_dict(proData)
            errors, warnings = cfg.validate()
            for config_name, warning in warnings:
                log.warning(f"  -> Config value: '{config_name}' in project '{project_name}'. Warning: {warning}")
            for config_name, error in errors:
                log.error(f"  -> Config value: '{config_name}' in project '{project_name}'. Error: {error}")

            if len(errors) > 0:
                raise exceptions.Abort(f"Aborted with {len(errors)} Configuration Errors!")
            elif strict and len(warnings) > 0:
                raise exceptions.Abort(f"Aborted with {len(warnings)} Configuration Warnings in 'strict' mode!")

        def tempDir(siteDir: str, tempDir: str, projectName: str) -> str:
            tempDoxyDir = PurePath.joinpath(Path(siteDir), Path(tempDir), Path(projectName))
            tempDoxyDir.mkdir(parents=True, exist_ok=True)
            return str(tempDoxyDir)

        self.doxygen = {}
        self.generatorBase = {}
        self.projects_config: dict[str, dict[str, any]] = self.config["projects"]
        self.debug = self.config.get("debug", False)

        # generate automatic documentation and append files in the list of files to be processed by mkdocs
        self.defaultTemplateConfig: dict = {
            "indent_level": 0,
        }

        log.info(f"Start plugin {pluginName}")

        for project_name, project_data in self.projects_config.items():
            log.info(f"-> Start project '{project_name}'")

            # Check project config -> raise exceptions
            checkConfig(self.config_project, project_data, config["strict"])

            if self.config.get("save-api"):
                tempDirApi = tempDir("", self.config.get("save-api"), project_name)
            else:
                tempDirApi = tempDir(config["site_dir"], "assets/.doxy/", project_name)

            # Check src changes -> run Doxygen
            doxygenRun = DoxygenRun(
                self.config["doxygen-bin-path"],
                project_data.get("src-dirs"),
                tempDirApi,
                project_data.get("doxy-cfg", {}),
                project_data.get("doxy-cfg-file", ""),
            )
            if doxygenRun.checkAndRun():
                log.info("  -> generating Doxygen files")
            else:
                log.info("  -> skip generating Doxygen files (nothing changes)")

            # Parse XML to basic structure
            cache = Cache()
            parser = XmlParser(cache=cache, debug=self.debug)

            # Parse basic structure to recursive Nodes
            self.doxygen[project_name] = Doxygen(doxygenRun.getOutputFolder(), parser=parser, cache=cache)

            # Print parsed files
            if self.debug:
                self.doxygen[project_name].printStructure()

            # Prepare generator for future use (GeneratorAuto, SnippetGenerator)
            self.generatorBase[project_name] = GeneratorBase(
                project_data.get("template-dir", ""),
                ignore_errors=self.config["ignore-errors"],
                debug=self.debug,
            )

            if self.config["full-doc"] and project_data.get("full-doc", True):
                generatorAuto = GeneratorAuto(
                    generatorBase=self.generatorBase[project_name],
                    tempDoxyDir=tempDirApi,
                    siteDir=config["site_dir"],
                    apiPath=project_data.get("api-path", project_name),
                    doxygen=self.doxygen[project_name],
                    useDirectoryUrls=config["use_directory_urls"],
                )

                project_config = self.defaultTemplateConfig.copy()
                project_config.update(project_data)
                generatorAuto.fullDoc(project_config)

                generatorAuto.summary(project_config)

                for file in generatorAuto.fullDocFiles:
                    files.append(file)
        return files

    def on_page_markdown(
        self,
        markdown: str,
        page: pages.Page,
        config: base.Config,
        files: files.Files,
    ) -> str:
        """! Generate snippets and append them to the markdown.
        @details

        @param markdown (str): The markdown.
        @param page (Page): The MkDocs page.
        @param config (Config): The MkDocs config.
        @param files (Files): The MkDocs files.
        @return: (str) The markdown.
        """
        if not self.is_enabled():
            return markdown

        # update default template config with page meta
        page_config = self.defaultTemplateConfig.copy()
        page_config.update(page.meta)

        generatorSnippets = GeneratorSnippets(
            markdown=markdown,
            generatorBase=self.generatorBase,
            doxygen=self.doxygen,
            projects=self.projects_config,
            useDirectoryUrls=config["use_directory_urls"],
            page=page,
            config=page_config,
            debug=self.debug,
        )

        return generatorSnippets.generate()


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
# def on_pre_build(self, config: base.Config):
#     return
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
