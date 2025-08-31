from __future__ import annotations

from xml.etree.ElementTree import Element as Element

from mkdoxy.cache import Cache
from mkdoxy.markdown import (
    Br,
    Code,
    MdBlockEquation,
    MdBlockQuote,
    MdBold,
    MdCodeBlock,
    MdHeader,
    MdImage,
    MdInlineEquation,
    MdItalic,
    MdLink,
    MdList,
    MdParagraph,
    MdRenderer,
    MdTable,
    MdTableCell,
    MdTableRow,
    Renderable,
    Text,
)
from mkdoxy.utils import lookahead

# https://www.doxygen.nl/manual/commands.html
SIMPLE_SECTIONS = {
    "see": "See also:",
    "note": "Note:",
    "bug": "Bug:",
    "warning": "Warning:",
    "return": "Returns:",
    "returns": "Returns:",
    "param": "Parameters:",
    "templateparam": "Template parameters:",
    "retval": "Return value:",
    "author": "Author:",
    "authors": "Authors:",
    "since": "Since:",
    "pre": "Precondition:",
    "remark": "Remark:",
    "copyright": "Copyright:",
    "post": "Postcondition:",
    "rcs": "Rcs:",
    "attention": "Attention:",
    "invariant": "Invariant:",
    "exception": "Exception:",
    "date": "Date:",
    "version": "Version:",
    "par": "\r\n",
}


class XmlParser:
    def __init__(self, cache: Cache, debug: bool = False) -> None:
        self.cache = cache
        self.debug = debug

    def anchor(self, name: str) -> str:
        return f'<a name="{name}"></a>'

    def paras_as_str(self, p: Element | None, italic: bool = False, plain: bool = False) -> str:
        if p is None:
            return ""
        if plain:
            return self.plain_as_str(p)
        renderer = MdRenderer()
        for m in self.paras(p, italic=italic):
            m.render(renderer, "")
        return renderer.output

    def reference_as_str(self, p: Element | None) -> str:
        if p is None:
            return ""
        renderer = MdRenderer()
        refid = p.get("refid")
        if refid is None:
            return p.text or ""
        m = MdLink([MdBold([Text(p.text or "")])], refid)
        m.render(renderer, "")
        return renderer.output

    def programlisting_as_str(self, p: Element | None) -> str:
        if p is None:
            return ""
        renderer = MdRenderer()
        for m in self.programlisting(p):
            m.render(renderer, "")
        return renderer.output

    def plain_as_str(self, p: Element | None) -> str:
        return " ".join(self.plain(p)).strip()

    def plain(self, p: Element | None) -> list[str]:
        ret = []
        if p is None:
            return []
        if p.text is not None:
            ret.append(p.text.strip())
        for item in list(p):
            ret.extend(self.plain(item))
        if p.tail is not None:
            ret.append(p.tail.strip())
        return ret

    def programlisting(self, p: Element | None) -> list[Renderable]:
        ret: list[Renderable] = []
        if p is None:
            return ret
        # programlisting
        if p.tag == "programlisting":
            code = MdCodeBlock([])
            for codeline in p.findall("codeline"):
                line = ""
                for highlight in codeline.findall("highlight"):
                    if highlight.text is not None:
                        line += highlight.text
                    for c in list(highlight):
                        if c.tag == "sp":
                            line += " "
                        if c.text:
                            line += c.text
                        if c.tail:
                            line += c.tail
                code.append(line)
            ret.extend((Text("\n"), code))
        return ret

    def paras(  # noqa: C901
        self, p: Element | None, italic: bool = False
    ) -> list[Renderable]:
        ret: list[Renderable] = []
        if p is None:
            return []
        if p.text is not None:
            if italic:
                ret.extend((MdItalic([Text(p.text.strip())]), Text(" ")))
            else:
                ret.append(Text(p.text))
        for item in list(p):
            # para
            if item.tag == "para":
                ret.extend((MdParagraph(self.paras(item)), Text("\n")))
            elif item.tag == "image":
                url = item.get("name")
                if url:
                    ret.append(MdImage(url))

            elif item.tag == "computeroutput":
                text_parts = []
                if item.text:
                    text_parts.append(item.text)
                for i in list(item):
                    text_parts.extend(self.plain(i))
                ret.append(Code(" ".join(text_parts)))

            elif item.tag == "programlisting":
                ret.extend(self.programlisting(item))

            elif item.tag == "table":
                t = MdTable()
                for row in item.findall("row"):
                    r = MdTableRow([])
                    for cell in row.findall("entry"):
                        for para in cell.findall("para"):
                            r.append(MdTableCell(self.paras(para)))
                    t.append(r)
                ret.append(t)

            elif item.tag == "blockquote":
                b = MdBlockQuote([])
                for para in item.findall("para"):
                    b.extend(self.paras(para))
                ret.append(b)

            elif item.tag == "heading":
                level = item.get("level")
                if level:
                    ret.append(MdHeader(int(level), self.paras(item)))

            elif item.tag in ["orderedlist", "itemizedlist"]:
                lst = MdList([])
                for listitem in item.findall("listitem"):
                    para_item = MdParagraph([])
                    for para in listitem.findall("para"):
                        para_item.extend(self.paras(para))
                    lst.append(para_item)
                ret.append(lst)

            elif item.tag == "ref":
                refid = item.get("refid")
                if refid:
                    try:
                        ref = self.cache.get(refid)
                        if italic:
                            if item.text:
                                ret.append(MdLink([MdItalic([MdBold([Text(item.text)])])], ref.url))
                            else:
                                ret.append(
                                    MdLink(
                                        [MdItalic([MdBold([Text(ref.get_full_name())])])],
                                        ref.url,
                                    )
                                )
                        elif item.text:
                            ret.append(MdLink([MdBold([Text(item.text)])], ref.url))
                        else:
                            ret.append(MdLink([MdBold([Text(ref.get_full_name())])], ref.url))
                    except KeyError:
                        if item.text:
                            ret.append(Text(item.text))

            elif item.tag == "sect1":
                title_elem = item.find("title")
                if title_elem is not None and title_elem.text:
                    ret.append(MdHeader(2, [Text(title_elem.text)]))
                ret.extend(self.paras(item))

            elif item.tag == "sect2":
                title_elem = item.find("title")
                if title_elem is not None and title_elem.text:
                    ret.append(MdHeader(3, [Text(title_elem.text)]))
                ret.extend(self.paras(item))

            elif item.tag == "sect3":
                title_elem = item.find("title")
                if title_elem is not None and title_elem.text:
                    ret.append(MdHeader(4, [Text(title_elem.text)]))
                ret.extend(self.paras(item))

            elif item.tag == "sect4":
                title_elem = item.find("title")
                if title_elem is not None and title_elem.text:
                    ret.append(MdHeader(5, [Text(title_elem.text)]))
                ret.extend(self.paras(item))

            elif item.tag == "sect5":
                title_elem = item.find("title")
                if title_elem is not None and title_elem.text:
                    ret.append(MdHeader(6, [Text(title_elem.text)]))
                ret.extend(self.paras(item))

            elif item.tag == "variablelist":
                varlistentry = item.find("varlistentry")
                if varlistentry is not None:
                    term = varlistentry.find("term")
                    if term is not None:
                        ret.append(MdHeader(4, self.paras(term)))

                    for listitem in item.findall("listitem"):
                        ret.extend(MdParagraph(self.paras(para)) for para in listitem.findall("para"))
            elif item.tag == "parameterlist":
                parameteritems = item.findall("parameteritem")
                lst = MdList([])
                for parameteritem in parameteritems:
                    param_name_list = parameteritem.find("parameternamelist")
                    if param_name_list is not None:
                        name = param_name_list.find("parametername")
                    else:
                        name = None

                    param_desc = parameteritem.find("parameterdescription")
                    if param_desc is not None:
                        description = param_desc.findall("para")
                    else:
                        description = []

                    par = MdParagraph([])
                    if name is not None and name.text:
                        par.extend(self.paras(name))
                    elif name is not None:
                        par.append(Code(name.text or ""))
                    par.append(Text(" "))
                    for ip in description:
                        par.extend(self.paras(ip))
                    lst.append(par)
                kind = item.get("kind")
                if kind:
                    ret.extend((Br(), MdBold([Text(SIMPLE_SECTIONS[kind])]), Br(), lst))
            elif item.tag == "simplesect":
                kind = item.get("kind")
                if kind:
                    ret.extend((Br(), MdBold([Text(SIMPLE_SECTIONS[kind])])))
                    if kind != "see":
                        ret.append(Br())
                    else:
                        ret.append(Text(" "))

                for sp, has_more in lookahead(item.findall("para")):
                    ret.extend(self.paras(sp))
                    if kind == "see":
                        if has_more:
                            ret.append(Text(", "))
                    else:
                        ret.append(Br())

            elif item.tag == "xrefsect":
                xreftitle = item.find("xreftitle")
                xrefdescription = item.find("xrefdescription")
                if xreftitle is not None and xreftitle.text:
                    kind = xreftitle.text.lower()
                    ret.extend((Br(), MdBold(self.paras(xreftitle)), Br()))
                if xrefdescription is not None:
                    for sp in xrefdescription.findall("para"):
                        ret.extend(self.paras(sp))
                        ret.append(Br())

            elif item.tag == "ulink":
                url = item.get("url")
                if url:
                    ret.append(MdLink(self.paras(item), url))

            elif item.tag == "bold":
                ret.append(MdBold(self.paras(item)))

            elif item.tag == "emphasis":
                ret.append(MdItalic(self.paras(item)))
            elif item.tag == "formula":
                if item.text is not None:
                    equation = item.text.strip("$ ")
                    if len(p) == 1 and item.tail is None:
                        ret.append(MdBlockEquation(equation))
                    else:
                        ret.append(MdInlineEquation(equation))

            if item.tail is not None:
                if italic:
                    ret.extend((Text(" "), MdItalic([Text(item.tail.strip())])))
                else:
                    ret.append(Text(item.tail))
        return ret
