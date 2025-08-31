from typing import Protocol


def escape(s: str) -> str:
    ret = s.replace("*", "\\*")
    ret = ret.replace("_", "\\_")
    ret = ret.replace("<", "&lt;")
    ret = ret.replace(">", "&gt;")
    return ret.replace("|", "\\|")


class MdRenderer:
    def __init__(self) -> None:
        self.output = ""
        self.eol_flag = True

    def write(self, s: str) -> None:
        self.output += s
        self.eol_flag = False

    def eol(self) -> None:
        if not self.eol_flag:
            self.output += "\n"
            self.eol_flag = True


class Renderable(Protocol):
    def render(self, f: MdRenderer, indent: str) -> None: ...

    @property
    def children(self) -> list["Renderable"]: ...


class Md:
    def __init__(self, children: list[Renderable]) -> None:
        self.children = children

    def append(self, child: Renderable) -> None:
        self.children.append(child)

    def extend(self, child: list[Renderable]) -> None:
        self.children.extend(child)

    def render(self, f: MdRenderer, indent: str) -> None:
        for child in self.children:
            child.render(f, indent)


class Text:
    def __init__(self, text: str) -> None:
        self.text = text
        self.children: list[Renderable] = []

    def render(self, f: MdRenderer, indent: str) -> None:
        if self.text:
            f.write(escape(self.text))


class Br:
    def __init__(self) -> None:
        self.children: list[Renderable] = []

    def render(self, f: MdRenderer, indent: str) -> None:
        f.write("\n\n")


class MdHint(Md):
    def __init__(self, children: list[Renderable], typ: str, title: str) -> None:
        Md.__init__(self, children)
        self.title = title
        self.typ = typ

    def render(self, f: MdRenderer, indent: str) -> None:
        f.write(f"::: {self.typ} {self.title}" + "\n")
        for child in self.children:
            child.render(f, "")
        f.write(":::\n")


class MdBold(Md):
    def __init__(self, children: list[Renderable]) -> None:
        Md.__init__(self, children)

    def render(self, f: MdRenderer, indent: str) -> None:
        f.write("**")
        for child in self.children:
            child.render(f, "")
        f.write("**")


class MdImage:
    def __init__(self, url: str) -> None:
        self.url = url
        self.children: list[Renderable] = []

    def render(self, f: MdRenderer, indent: str) -> None:
        f.write(f"![Image]({self.url})")


class Code:
    def __init__(self, text: str) -> None:
        self.text = text
        self.children: list[Renderable] = []

    def render(self, f: MdRenderer, indent: str) -> None:
        f.write(f"`{self.text}`")


class MdCodeBlock:
    def __init__(self, lines: list[str]) -> None:
        self.lines = lines
        self.children: list[Renderable] = []

    def append(self, line: str) -> None:
        self.lines.append(line)

    def render(self, f: MdRenderer, indent: str) -> None:
        f.write("```\n")
        for line in self.lines:
            f.write(line)
            f.write("\n")
        f.write("```\n")


class MdBlockQuote(Md):
    def __init__(self, children: list[Renderable]) -> None:
        Md.__init__(self, children)

    def render(self, f: MdRenderer, indent: str) -> None:
        f.write("\n")
        for child in self.children:
            f.write("> ")
            child.render(f, "")
            f.write("\n")


class MdItalic(Md):
    def __init__(self, children: list[Renderable]) -> None:
        Md.__init__(self, children)

    def render(self, f: MdRenderer, indent: str) -> None:
        f.write("_")
        for child in self.children:
            child.render(f, "")
        f.write("_")


class MdParagraph(Md):
    def __init__(self, children: list[Renderable]) -> None:
        Md.__init__(self, children)

    def render(self, f: MdRenderer, indent: str) -> None:
        for child in self.children:
            child.render(f, indent)
        f.eol()


class MdLink(Md):
    def __init__(self, children: list[Renderable], url: str) -> None:
        Md.__init__(self, children)
        self.url = url

    def render(self, f: MdRenderer, indent: str) -> None:
        f.write("[")
        for child in self.children:
            child.render(f, "")
        f.write(f"]({self.url})")


class MdList(Md):
    def __init__(self, children: list[Renderable]) -> None:
        Md.__init__(self, children)

    def render(self, f: MdRenderer, indent: str) -> None:
        f.eol()
        for child in self.children:
            if not isinstance(child, MdList):
                f.write(f"{indent}* ")
            child.render(f, f"{indent}  ")


class MdLine:
    def __init__(self) -> None:
        self.children: list[Renderable] = []

    def render(self, f: MdRenderer, indent: str) -> None:
        f.eol()
        f.write("----------------------------------------")
        f.eol()


class MdHeader(Md):
    def __init__(self, level: int, children: list[Renderable]) -> None:
        Md.__init__(self, children)
        self.level = level

    def render(self, f: MdRenderer, indent: str) -> None:
        f.write("#" * self.level + " ")
        for child in self.children:
            child.render(f, f"{indent}")
        f.write("\n")
        f.eol()


class MdTableCell(Md):
    def __init__(self, children: list[Renderable]) -> None:
        Md.__init__(self, children)

    def render(self, f: MdRenderer, indent: str) -> None:
        for child in self.children:
            child.render(f, indent)


class MdTableRow(Md):
    def __init__(self, children: list[Renderable]) -> None:
        Md.__init__(self, children)

    def render(self, f: MdRenderer, indent: str) -> None:
        f.eol()
        f.write("|")
        for child in self.children:
            child.render(f, "")
            f.write("|")
        f.eol()


class MdTable(Md):
    def __init__(self) -> None:
        Md.__init__(self, [])

    def render(self, f: MdRenderer, indent: str) -> None:
        is_first = True
        f.eol()
        for child in self.children:
            child.render(f, "")
            if is_first:
                for _ in range(len(child.children)):
                    f.write("|-----")
                f.write("|")
            is_first = False
        f.write("\n\n")


class MdInlineEquation(Md):
    def __init__(self, equation: str) -> None:
        super().__init__([])
        self.equation = equation

    def render(self, f: MdRenderer, indent: str) -> None:
        if self.equation:
            f.write(rf"\({self.equation}\)")


class MdBlockEquation(Md):
    def __init__(self, equation: str) -> None:
        super().__init__([])
        self.equation = equation

    def render(self, f: MdRenderer, indent: str) -> None:
        f.write("\n")
        f.write(rf"\[{self.equation}\]")
        f.write("\n")
