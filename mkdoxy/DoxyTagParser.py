import re


class DoxyTagParser:
    def __init__(self, markdown_page: str, debug: bool = False):
        self.markdown_page = markdown_page
        self.debug = debug
        self.doxy_key = "::: doxy"
        self.indent = "(?P<indent>[\t ]*)"
        self.project = "(?P<project>[a-zA-Z]+)"
        self.key = "(?P<key>[a-zA-Z.-_]+)"
        self.dot = "\."
        self.optional_dot = "[.]?"
        self.look_ahead = "(?=\n)"  # it's a look ahead because we don't want to capture the newline

    def replaceMarkdown(self, start: int, end: int, replace_format: str, **kwargs):
        self.markdown_page = self.markdown_page.replace(self.markdown_page[start:end], replace_format.format(**kwargs))

    def returnMarkdown(self):
        return self.markdown_page

    def parseEmptyTag(self, replacement: str):
        empty_tag = (
            rf"{self.indent}{self.doxy_key}{self.optional_dot}{self.look_ahead}"  # https://regex101.com/r/Zh38uo/1
        )
        matches = re.finditer(empty_tag, self.markdown_page, re.MULTILINE)
        for match in reversed(list(matches)):
            self.replaceMarkdown(match.start(), match.end(), replacement, indent=match.group("indent"))

    def parseProject(self, replacement: str):
        project_tag = rf"{self.indent}{self.doxy_key}{self.dot}{self.project}{self.optional_dot}{self.look_ahead}"  # https://regex101.com/r/TfAsmE/1
        matches = re.finditer(project_tag, self.markdown_page, re.MULTILINE)
        for match in reversed(list(matches)):
            self.replaceMarkdown(
                match.start(),
                match.end(),
                replacement,
                indent=match.group("indent"),
                project=match.group("project"),
            )

    def parseProjectTagSingle(self, replacement: str):
        project_tag = (
            rf"{self.indent}{self.doxy_key}{self.dot}{self.project}{self.dot}(?P<key>[a-zA-Z-_]+){self.look_ahead}"
        )
        matches = re.finditer(project_tag, self.markdown_page, re.MULTILINE)
        for match in reversed(list(matches)):
            self.replaceMarkdown(
                match.start(),
                match.end(),
                replacement,
                project=match.group("project"),
                key=match.group("key"),
            )

    def parseProjectTagMulti(self, replacement: str):
        project_tag = rf"{self.indent}{self.doxy_key}{self.dot}{self.project}{self.dot}(?P<key>[a-zA-Z-_]+)\s*\n(?:(?=\n)|(?=:::)|\Z)"  # noqa: E501
        matches = re.finditer(project_tag, self.markdown_page, re.MULTILINE)
        for match in reversed(list(matches)):
            list_keys = match.group("key").split(".")  # split keys by . to allow for nested keys
            self.replaceMarkdown(
                match.start(),
                match.end(),
                replacement,
                project=match.group("project"),
                keys=list_keys,
            )
