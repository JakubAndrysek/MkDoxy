import logging
import pathlib
import re

import yaml
from mkdocs.structure import pages

from mkdoxy.doxygen import Doxygen
from mkdoxy.finder import Finder
from mkdoxy.generator_base import GeneratorBase
from mkdoxy.node import Node

log: logging.Logger = logging.getLogger("mkdocs")

regex_incorrect = r"(?s)(?<!```yaml\n)(^::: doxy)(\.(?P<project>[a-zA-Z0-9_]+))?[\.]?[\s]*\n(?P<yaml>.*?)\s*\n(?:(?=\n)|(?=:::)|\Z)"  # https://regex101.com/r/IYl25b/2  # noqa: E501
regex_long = r"(?s)(?<!```yaml\n)(^::: doxy\.(?P<project>[a-zA-Z0-9_]+)\.(?P<argument>[a-zA-Z0-9_.]+))\s*\n(?P<yaml>.*?)(?:(?:(?:\r*\n)(?=\n))|(?=:::)|`|\Z)"  # https://regex101.com/r/lIgOij/4  # noqa: E501
regex_short = r"(?s)(?<!```yaml\n)(^::: doxy\.(?P<project>[a-zA-Z0-9_]+)\.(?P<argument>[a-zA-Z0-9_.]+))\s*\n(?:(?=\n)|(?=:::)|\Z)"  # https://regex101.com/r/QnqxRc/2  # noqa: E501


class GeneratorSnippets:
    def __init__(
        self,
        markdown: str,
        generator_base: dict[str, GeneratorBase],
        doxygen: dict[str, Doxygen],
        projects: dict[str, dict[str, any]],
        use_directory_urls: bool,
        page: pages.Page,
        config: dict,
        debug: bool = False,
    ):
        self.markdown = markdown
        self.generator_base = generator_base
        self.doxygen = doxygen
        self.projects = projects
        self.use_directory_urls = use_directory_urls
        self.page = page
        self.config = config
        self.debug = debug
        self.finder = Finder(doxygen, debug)

        self.doxy_arguments = {
            "code": self.doxy_code,
            "function": self.doxy_function,
            "class": self.doxy_class,
            "class.method": self.doxy_class_method,
            "class.list": self.doxy_class_list,
            "class.index": self.doxy_class_index,
            "class.hierarchy": self.doxy_class_hierarchy,
            "namespace.list": self.doxy_namespace_list,
            "file.list": self.doxy_file_list,
        }

        # fix absolute path
        path = pathlib.PurePath(self.page.url).parts
        self.page_url_prefix = "".join("../" for _ in range(len(path) - 1))

    def generate(self):
        if self.is_doxy_inactive(self.config):
            return self.markdown  # doxygen is inactive return unchanged markdown

        try:
            matches = re.finditer(regex_incorrect, self.markdown, re.MULTILINE)
            for match in reversed(list(matches)):
                snippet = match.group()
                project_name = match.group("project") or "<project_name>"

                snippet_config = self.config.copy()
                snippet_config.update(self.try_load_yaml(match.group("yaml"), project_name, snippet, self.config))

                if self.is_doxy_inactive(snippet_config):
                    continue

                replacement = (
                    self.incorrect_argument(project_name, "", snippet_config, snippet)
                    if self.is_project_exist(project_name)
                    else self.incorrect_project(project_name, snippet_config, snippet)
                )
                self.replace_markdown(match.start(), match.end(), replacement)

            matches = re.finditer(regex_short, self.markdown, re.MULTILINE)
            for match in reversed(list(matches)):
                snippet = match.group()
                argument = match.group("argument").lower()
                project_name = match.group("project")

                snippet_config = self.config.copy()
                snippet_config.update(self.try_load_yaml(match.group("yaml"), project_name, snippet, self.config))

                if self.is_doxy_inactive(snippet_config):
                    continue

                replace_str = self.call_doxy_by_name(snippet, project_name, argument, snippet_config)
                self.replace_markdown(match.start(), match.end(), replace_str)

            matches = re.finditer(regex_long, self.markdown, re.MULTILINE)
            for match in reversed(list(matches)):
                snippet = match.group()
                argument = match.group("argument").lower()
                project_name = match.group("project")
                # log.debug(f"\nArgument: {argument}")

                # config has been updated by yaml
                snippet_config = self.config.copy()
                snippet_config.update(self.try_load_yaml(match.group("yaml"), project_name, snippet, self.config))

                replace_str = self.call_doxy_by_name(snippet, project_name, argument, snippet_config)
                self.replace_markdown(match.start(), match.end(), replace_str)
            return self.markdown
        except Exception as e:
            basename = pathlib.Path(__file__).name
            log.error(f"Error in {self.page.url} page. Incorrect doxy snippet or error in file {basename}")
            log.error(f"Error: {e}")
            return self.markdown

    def try_load_yaml(self, yaml_raw: str, project: str, snippet: str, config: dict) -> dict:
        try:
            return yaml.safe_load(yaml_raw)
        except yaml.YAMLError:
            log.error(f"YAML error in {project} project on page {self.page.url}")
            self.doxy_error(
                project,
                config,
                "YAML error",
                "Check your YAML syntax",
                "YAML snippet:",
                yaml_raw,
                "yaml",
                snippet,
            )
            return {}

    def incorrect_project(
        self,
        project: str,
        config: dict,
        snippet: str,
    ) -> str:
        return self.doxy_error(
            project,
            config,
            f"Incorrect project name: {project}",
            "Project name have to contain [a-zA-Z0-9_]",
            "A list of available projects:",
            "\n".join(self.projects.keys()),
            "yaml",
            snippet,
        )

    def incorrect_argument(self, project: str, argument: str, config: dict, snippet: str) -> str:
        return self.doxy_error(
            project,
            config,
            f"Incorrect argument: {argument}" if argument else f"Add argument to snippet: {project}",
            f"Argument have to be based on this diagram → **:::doxy.{project}.<argument\\>**",
            "A list of available arguments:",
            "\n".join(self.doxy_arguments.keys()),
            "yaml",
            snippet,
        )

    def replace_markdown(self, start: int, end: int, replacement: str):
        self.markdown = self.markdown[:start] + replacement + "\n" + self.markdown[end:]

    def _set_link_prefix_node(self, node: Node, linkPrefix: str):
        node.project.link_prefix = linkPrefix

    def _set_link_prefix_nodes(self, nodes: list[Node], linkPrefix: str):
        if nodes:
            nodes[0].project.link_prefix = linkPrefix

    def is_project_exist(self, project: str):
        return project in self.projects

    def is_doxy_inactive(self, config: dict):
        return config.get("disable_doxy_snippets", False)

    def call_doxy_by_name(self, snippet, project: str, argument: str, config: dict) -> str:
        if argument not in self.doxy_arguments:
            return self.incorrect_argument(project, argument, config, snippet)
        callback = self.doxy_arguments[argument]
        return callback(snippet, project, config)

    def check_config(self, snippet, project: str, config, required_params: [str]) -> bool:
        """
        returns false if config is correct
        return error message if project not exist or find problem in config
        """
        return next(
            (
                self.doxy_error(
                    project,
                    config,
                    f"Missing parameter: {param}",
                    "This parameter is required",
                    "Required parameters:",
                    "\n".join(required_params),
                    "yaml",
                    snippet,
                )
                for param in required_params
                if not config.get(param)
            ),
            False,
        )

    ### Create documentation generator callbacks

    def doxy_error(
        self,
        project,
        config: dict,
        title: str,
        description: str,
        code_header: str = "",
        code: str = "",
        code_language: str = "",
        snippet_code: str = "",
    ) -> str:
        log.error(f"  -> {title} -> page: {self.page.canonical_url}")
        if project not in self.projects:
            project = list(self.projects)[0]
        return self.generator_base[project].error(
            config, title, description, code_header, code, code_language, snippet_code
        )

    def doxy_code(self, snippet, project: str, config):
        error_msg = self.check_config(snippet, project, config, ["file"])
        if error_msg:
            return error_msg
        node = self.finder.doxy_code(project, config.get("file"))
        if node is None:
            return self.doxy_node_is_none(project, config, snippet)

        if isinstance(node, Node):
            prog_code = self.code_strip(
                node.programlisting,
                node.code_language,
                config.get("start", 1),
                config.get("end", 0),
            )
            if prog_code is False:
                return self.doxy_error(
                    project,
                    config,
                    f"Parameter start: {config.get('start')} is greater than end: {config.get('end')}",
                    f"{snippet}",
                    "yaml",
                )
            self._set_link_prefix_node(node, self.page_url_prefix + project + "/")
            return self.generator_base[project].code(node, config, prog_code)
        return self.doxy_error(
            project,
            config,
            f"Did not find File: `{config.get('file')}`",
            "Check your file name",
            f"Available files in {project} project:",
            "\n".join(node),
            "yaml",
            snippet,
        )

    def code_strip(self, code_raw, code_language: str, start: int = 1, end: int = None):
        lines = code_raw.split("\n")

        if end and start > end:
            return False

        out = "".join(line + "\n" for num, line in enumerate(lines) if num >= start and (num <= end or end == 0))
        return f"```{code_language} linenums='{start}'\n{out}```"

    def doxy_function(self, snippet, project: str, config: dict):
        error_msg = self.check_config(snippet, project, config, ["name"])
        if error_msg:
            return error_msg

        node = self.finder.doxy_function(project, config.get("name"))
        if node is None:
            return self.doxy_node_is_none(project, config, snippet)

        if isinstance(node, Node):
            self._set_link_prefix_node(node, self.page_url_prefix + project + "/")
            return self.generator_base[project].function(node, config)
        return self.doxy_error(
            project,
            config,
            "Incorrect function configuration",
            f"Did not find Function with name: `{config.get('name')}`",
            "Available functions:",
            "\n".join(node),
            "yaml",
            snippet,
        )

    def doxy_class(self, snippet, project: str, config: dict):
        error_msg = self.check_config(snippet, project, config, ["name"])
        if error_msg:
            return error_msg

        node = self.finder.doxy_class(project, config.get("name"))
        if node is None:
            return self.doxy_node_is_none(project, config, snippet)

        if isinstance(node, Node):
            self._set_link_prefix_node(node, self.page_url_prefix + project + "/")
            return self.generator_base[project].member(node, config)
        return self.doxy_error(
            project,
            config,
            "Incorrect class configuration",
            f"Did not find Class with name: `{config.get('name')}`",
            "Available classes:",
            "\n".join(node),
            "yaml",
            snippet,
        )

    def doxy_class_method(self, snippet, project: str, config):
        error_msg = self.check_config(snippet, project, config, ["name", "method"])
        if error_msg:
            return error_msg

        node = self.finder.doxy_class_method(project, config.get("name"), config.get("method"))
        if node is None:
            return self.doxy_node_is_none(project, config, snippet)

        if isinstance(node, Node):
            self._set_link_prefix_node(node, self.page_url_prefix + project + "/")
            return self.generator_base[project].function(node, config)
        return self.doxy_error(
            project,
            config,
            "Incorrect class method configuration",
            f"Did not find Class with name: `{config.get('name')}` and method: `{config.get('method')}`",
            "Available classes and methods:",
            "\n".join(node),
            "yaml",
            snippet,
        )

    def doxy_class_list(self, snippet, project: str, config):
        error_msg = self.check_config(snippet, project, config, [])
        if error_msg:
            return error_msg
        nodes = self.doxygen[project].root.children
        self._set_link_prefix_nodes(nodes, self.page_url_prefix + project + "/")
        return self.generator_base[project].annotated(nodes, config)

    def doxy_class_index(self, snippet, project: str, config):
        error_msg = self.check_config(snippet, project, config, [])
        if error_msg:
            return error_msg
        nodes = self.doxygen[project].root.children
        self._set_link_prefix_nodes(nodes, self.page_url_prefix + project + "/")
        return self.generator_base[project].classes(nodes, config)

    def doxy_class_hierarchy(self, snippet, project: str, config):
        error_msg = self.check_config(snippet, project, config, [])
        if error_msg:
            return error_msg
        nodes = self.doxygen[project].root.children
        self._set_link_prefix_nodes(nodes, self.page_url_prefix + project + "/")
        return self.generator_base[project].hierarchy(nodes, config)

    def doxy_namespace_list(self, snippet, project: str, config):
        error_msg = self.check_config(snippet, project, config, [])
        if error_msg:
            return error_msg
        nodes = self.doxygen[project].root.children
        self._set_link_prefix_nodes(nodes, self.page_url_prefix + project + "/")
        return self.generator_base[project].namespaces(nodes, config)

    def doxy_file_list(self, snippet, project: str, config):
        error_msg = self.check_config(snippet, project, config, [])
        if error_msg:
            return error_msg
        nodes = self.doxygen[project].files.children
        self._set_link_prefix_nodes(nodes, self.page_url_prefix + project + "/")
        return self.generator_base[project].fileindex(nodes, config)

    def doxy_node_is_none(self, project: str, config: dict, snippet: str) -> str:
        return self.doxy_error(
            project,
            config,
            f"Could not find coresponding snippet for project {project}",
            f"Config: {config}",
            "yaml",
            snippet,
        )


### Create documentation generator callbacks END


class SnippetClass:
    def __init__(self, config):
        self.config = config

    def default(self):
        return ""
