"""@package mkdoxy.plugin
MkDoxy → MkDocs + Doxygen = easy documentation generator with code snippets

MkDoxy is a MkDocs plugin for generating documentation from Doxygen XML files.
"""
import logging
import os
from pathlib import Path, PurePath
from urllib.parse import urlparse
from git import Repo, exc as GitExc

from mkdocs import exceptions
from mkdocs.config import Config, base, config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure import files, pages
from mkdocs.structure.nav import Navigation, get_navigation
from mkdoxy.cache import Cache
from mkdoxy.doxygen import Doxygen
from mkdoxy.doxyrun import DoxygenRun
from mkdoxy.generatorAuto import GeneratorAuto
from mkdoxy.generatorBase import GeneratorBase
from mkdoxy.generatorSnippets import GeneratorSnippets
from mkdoxy.xml_parser import XmlParser

import tempfile
import shutil
import yaml
import re

log: logging.Logger = logging.getLogger("mkdocs")
pluginName: str = "MkDoxy"


def clone_repository(url: str, recursive: bool = False, branch: str = "main") -> str:
    """! Clone a git repository and return the path
    @param url: Repository URL
    @param recursive: Clone submodules recursively
    @param branch: Branch to clone
    @return: Path to cloned repository
    """
    try:
        # Use mkdtemp to create a persistent temporary directory
        tmp_dir = tempfile.mkdtemp()
        repo_name = url.split('/')[-1].split('.')[0] or "repo"
        repo_path = str(Path(tmp_dir) / repo_name)
        
        clone_opts = {
            'url': url,
            'to_path': repo_path,
            'depth': 1,
            'branch': branch,
            'recursive': recursive
        }
        
        Repo.clone_from(**clone_opts)
        log.debug(f"Contents of cloned repository '{repo_name}': {os.listdir(repo_path)}")
        return str(repo_path)
        
    except GitExc.GitCommandError as e:
        error_message = f"Git clone failed for {url}: {(e.stderr or str(e)).strip()}"
        log.error(error_message)
        raise ConfigurationError(error_message)
        
    except Exception as e:
        error_message = f"An unexpected error occurred during git clone for {url}: {str(e)}"
        log.error(error_message)
        raise ConfigurationError(error_message)
    
class MkDoxy(BasePlugin):
    """! MkDocs plugin for generating documentation from Doxygen XML files."""

    # Config options for the plugin
    config_scheme = (
        ("projects", config_options.Type(dict, default={})),
        ("full-doc", config_options.Type(bool, default=True)),
        ("debug", config_options.Type(bool, default=False)),
        ("ignore-errors", config_options.Type(bool, default=False)),
        ("save-api", config_options.Type(str, default="")),
        ("git-recursive", config_options.Type(bool, default=False)),
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
        ("git-url", config_options.Type(str, default="")),
        ("git-branch", config_options.Type(str, default="main")),
        ("parent-nav-section", config_options.Type(str, default="", required=False)),
        ("landing-page-replaces", config_options.Type(str, default="", required=False)),
        ("landing-page", config_options.Type(str, default="", required=False)),
    )
    new_nav = None
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

        temp_dirs_to_cleanup: list[str] = []

        for project_name, project_data in self.projects_config.items():
            log.info(f"-> Start project '{project_name}'")

            # Handle Git repository if specified
            src_dirs = project_data.get("src-dirs")
            git_url = project_data.get("git-url", "")

            if git_url:
                try:
                    log.info(f"  -> cloning repository {git_url}")
                    cloned_path = clone_repository(
                        git_url,
                        recursive=self.config.get("git-recursive", False),
                        branch=project_data.get("git-branch", "main")
                    )
                    temp_dirs_to_cleanup.append(str(Path(cloned_path).parent))
                    log.debug(f"Contents of cloned repository: {os.listdir(cloned_path)}")
                    # Update src-dirs to use cloned repository
                    if isinstance(src_dirs, str):
                        project_data["src-dirs"] = str(Path(cloned_path) / src_dirs)
                    else:
                        project_data["src-dirs"] = str(Path(cloned_path))
                except Exception as e:
                    error_msg = f"Failed to clone repository {git_url}: {str(e)}"
                    if self.config["ignore-errors"]:
                        log.error(error_msg)
                        continue
                    else:
                        raise exceptions.ConfigurationError(error_msg)
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
                generatorAuto.copyImages()
                for file in generatorAuto.fullDocFiles:
                    files.append(file)
            parent_nav_section = project_data.get("parent-nav-section", "")
            if parent_nav_section:
                self.new_nav = rewrite_nav(
                    project_name,
                    parent_nav_section,
                    config["site_dir"],
                    files,
                    config,
                    landing_page_replaces=project_data.get("landing-page-replaces", ""),
                    landing_page=project_data.get("landing-page", ""),
                )
            else:
                log.debug(f"No 'parent-nav-section' set for project '{project_name}', skipping nav injection.")
        for temp_dir in temp_dirs_to_cleanup:
            cleanup_temp_dir(temp_dir)
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
    def on_nav(self, nav, config, files):
        return nav


def find_doxygen_index(doxy_dir: str, project_name: str):
    """! Determine the Doxygen landing page to use for 'landing-page-replaces'.
    @details Prefers a real Doxygen mainpage (indexpage.md). If none exists,
    falls back to the first related page listed in pages.md (typically the
    project's README overview).
    @return: (str|None) Path relative to the api-path (e.g. "proj/indexpage.md")
             or None if no landing page could be determined.
    """
    if os.path.isfile(os.path.join(doxy_dir, "indexpage.md")):
        return f"{project_name}/indexpage.md"

    pages_md = os.path.join(doxy_dir, "pages.md")
    if os.path.isfile(pages_md):
        link_pattern = re.compile(r'\[[^\]]*\]\(([^)]+\.md)\)')
        with open(pages_md, "r") as f:
            for line in f:
                match = link_pattern.search(line)
                if match:
                    return f"{project_name}/{match.group(1).strip()}"

    return None


def rewrite_nav(project_name, parent_nav_section, src_dirs, files, config, landing_page_replaces="", landing_page="") -> Navigation: 
    doxy_dir = f'{src_dirs}/assets/.doxy/{project_name}/{project_name}'
    with open(f'{doxy_dir}/links.md', 'r') as file:
        lines = file.read().splitlines()
    nav_entries = []
    index_path = None
    pattern = re.compile(r'-\s+\[([^\]]+)\]\(([^)]+)\)')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = pattern.search(line)
        if not match:
            continue

        title = match.group(1).strip()
        filename = match.group(2).strip()         
        path = f"{project_name}/{filename}"        

        nav_entries.append({title: path})

    # Determine the Doxygen "landing page" used for the optional nav override.
    # If 'landing-page' is set, use that path (a simple address in the docs
    # folder) directly. Otherwise fall back to a real Doxygen mainpage
    # (indexpage.md) or the first related page listed in pages.md.
    if landing_page_replaces:
        if landing_page:
            index_path = landing_page
        else:
            index_path = find_doxygen_index(doxy_dir, project_name)

    def find_and_insert_path(nav_list: list, section_path: list[str], entries: list) -> bool:
        """Traverse a raw nav list following a path of nested section names and insert entries at the end."""
        if not section_path:
            return False

        target = section_path[0]
        remaining = section_path[1:]

        for item in nav_list:
            if not isinstance(item, dict):
                continue
            for key, value in item.items():
                if key == target:
                    if not remaining:
                        if not isinstance(value, list):
                            item[key] = [value]
                        item[key].extend(entries)
                        return True
                    if isinstance(value, list):
                        if find_and_insert_path(value, remaining, entries):
                            return True
                
        return False

    def find_section_list(nav_list: list, section_path: list[str]):
        """Return the list of children under the given nested section path (or None)."""
        if not section_path:
            return None

        target = section_path[0]
        remaining = section_path[1:]

        for item in nav_list:
            if not isinstance(item, dict):
                continue
            for key, value in item.items():
                if key != target:
                    continue
                if not remaining:
                    if not isinstance(value, list):
                        item[key] = [value]
                    return item[key]
                if isinstance(value, list):
                    found = find_section_list(value, remaining)
                    if found is not None:
                        return found
        return None

    def replace_path_value(nav_list: list, target_path: str, new_path: str) -> bool:
        """Recursively replace the first nav entry whose value equals target_path,
        keeping its original title. Handles both titled entries ({title: path})
        and bare string entries (- path). Returns True if a replacement was made."""
        for index, item in enumerate(nav_list):
            # Bare string entry, e.g. "- manual/.../index.md" (no explicit title)
            if isinstance(item, str):
                if item == target_path:
                    nav_list[index] = new_path
                    return True
                continue
            if not isinstance(item, dict):
                continue
            for key, value in item.items():
                if value == target_path:
                    item[key] = new_path
                    return True
                if isinstance(value, list):
                    if replace_path_value(value, target_path, new_path):
                        return True
        return False

    section_path = [seg.strip() for seg in parent_nav_section.split("::")]

    raw_nav = config.get("nav") or []

    # Optionally override an existing nav entry (within the parent section only)
    # with the Doxygen mainpage, keeping the original title. This does not touch
    # the referenced file, so its other references in the nav stay intact.
    if landing_page_replaces and index_path:
        section_list = find_section_list(raw_nav, section_path)
        if section_list is None:
            log.warning(
                f"Parent nav section path '{parent_nav_section}' not found in navigation. "
                f"Cannot apply 'landing-page-replaces'."
            )
        elif replace_path_value(section_list, landing_page_replaces, index_path):
            # Don't add the mainpage again as a separate entry.
            nav_entries = [e for e in nav_entries if index_path not in e.values()]
            log.info(
                f"  -> landing-page-replaces: replaced '{landing_page_replaces}' with "
                f"Doxygen landing page '{index_path}' in section '{parent_nav_section}'"
            )
        else:
            log.warning(
                f"'landing-page-replaces' target '{landing_page_replaces}' not found within "
                f"section '{parent_nav_section}'. Mainpage will be added normally."
            )
    elif landing_page_replaces and not index_path:
        log.warning(
            f"'landing-page-replaces' is set for project '{project_name}', but no Doxygen "
            f"landing page (indexpage.md or a related page in pages.md) was found. "
            f"Nothing to override."
        )

    section_found = find_and_insert_path(raw_nav, section_path, nav_entries)

    if not section_found:
        log.warning(
            f"Parent nav section path '{parent_nav_section}' not found in navigation. "
            f"Searched path: {' -> '.join(section_path)}. New entries will not be added."
        )

    config["nav"] = raw_nav
    nav = get_navigation(files, config)
    return nav
    

def cleanup_temp_dir(temp_dir):
    """Remove the temporary directory created by mkdtemp."""
    shutil.rmtree(temp_dir)
    log.info(f"Temporary directory {temp_dir} removed.")

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
