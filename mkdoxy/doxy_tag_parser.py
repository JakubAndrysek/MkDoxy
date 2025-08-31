import re


class DoxyTagParser:
    def __init__(self, markdown_page: str, debug: bool = False) -> None:
        self.markdown_page = markdown_page
        self.debug = debug
        self.doxy_key = "::: doxy"
        self.indent = "(?P<indent>[\t ]*)"
        self.project = "(?P<project>[a-zA-Z]+)"
        self.key = "(?P<key>[a-zA-Z.-_]+)"
        self.dot = r"\."
        self.optional_dot = "[.]?"
        self.look_ahead = r"(?=\n)"  # look ahead to avoid capturing newline

    def replace_markdown(
        self, start: int, end: int, replace_format: str, **kwargs: str
    ) -> None:
        self.markdown_page = self.markdown_page.replace(
            self.markdown_page[start:end], replace_format.format(**kwargs)
        )

    def return_markdown(self) -> str:
        return self.markdown_page

    def parse_empty_tag(self, replacement: str) -> None:
        empty_tag = (
            rf"{self.indent}{self.doxy_key}{self.optional_dot}"
            rf"{self.look_ahead}"
        )  # https://regex101.com/r/Zh38uo/1
        matches = re.finditer(empty_tag, self.markdown_page, re.MULTILINE)
        for match in reversed(list(matches)):
            self.replace_markdown(
                match.start(),
                match.end(),
                replacement,
                indent=match.group("indent")
            )

    def parse_project(self, replacement: str) -> None:
        project_tag = (
            rf"{self.indent}{self.doxy_key}{self.dot}{self.project}"
            rf"{self.optional_dot}{self.look_ahead}"
        )  # https://regex101.com/r/TfAsmE/1
        matches = re.finditer(project_tag, self.markdown_page, re.MULTILINE)
        for match in reversed(list(matches)):
            self.replace_markdown(
                match.start(),
                match.end(),
                replacement,
                indent=match.group("indent"),
                project=match.group("project"),
            )

    def parse_project_tag_single(self, replacement: str) -> None:
        project_tag = (
            rf"{self.indent}{self.doxy_key}{self.dot}{self.project}"
            rf"{self.dot}(?P<key>[a-zA-Z-_]+){self.look_ahead}"
        )
        matches = re.finditer(project_tag, self.markdown_page, re.MULTILINE)
        for match in reversed(list(matches)):
            self.replace_markdown(
                match.start(),
                match.end(),
                replacement,
                project=match.group("project"),
                key=match.group("key"),
            )

    def parse_project_tag_multi(self, replacement: str) -> None:
        project_tag = rf"{self.indent}{self.doxy_key}{self.dot}{self.project}{self.dot}(?P<key>[a-zA-Z-_]+)\s*\n(?:(?=\n)|(?=:::)|\Z)"  # noqa: E501
        matches = re.finditer(project_tag, self.markdown_page, re.MULTILINE)
        for match in reversed(list(matches)):
            # split keys by . to allow for nested keys
            list_keys = match.group("key").split(".")
            self.replace_markdown(
                match.start(),
                match.end(),
                replacement,
                project=match.group("project"),
                keys=list_keys,
            )
