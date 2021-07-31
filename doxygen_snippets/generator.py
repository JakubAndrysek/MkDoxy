import os
import re
import string
import traceback
from typing import TextIO
from jinja2 import Template
from jinja2.exceptions import TemplateSyntaxError, TemplateError
from jinja2 import StrictUndefined, Undefined
from doxybook.node import Node, DummyNode
from doxybook.constants import Kind
from doxybook.templates.annotated import TEMPLATE as ANNOTATED_TEMPLATE
from doxybook.templates.member import TEMPLATE as MEMBER_TEMPLATE
from doxybook.templates.member_definition import TEMPLATE as MEMBER_DEFINITION_TEMPLATE
from doxybook.templates.member_table import TEMPLATE as MEMBER_TABLE_TEMPLATE
from doxybook.templates.namespaces import TEMPLATE as NAMESPACES_TEMPLATE
from doxybook.templates.classes import TEMPLATE as CLASSES_TEMPLATE
from doxybook.templates.hierarchy import TEMPLATE as HIEARARCHY_TEMPLATE
from doxybook.templates.index import TEMPLATE as INDEX_TEMPLATE
from doxybook.templates.modules import TEMPLATE as MODULES_TEMPLATE
from doxybook.templates.files import TEMPLATE as FILES_TEMPLATE
from doxybook.templates.programlisting import TEMPLATE as PROGRAMLISTING_TEMPLATE
from doxybook.templates.page import TEMPLATE as PAGE_TEMPLATE
from doxybook.templates.pages import TEMPLATE as PAGES_TEMPLATE

LETTERS = string.ascii_lowercase + '~_@'

ADDITIONAL_FILES = {
    'Namespace List': 'namespaces.md',
    'Namespace Members': 'namespace_members.md',
    'Namespace Member Functions': 'namespace_member_functions.md',
    'Namespace Member Variables': 'namespace_member_variables.md',
    'Namespace Member Typedefs': 'namespace_member_typedefs.md',
    'Namespace Member Enumerations': 'namespace_member_enums.md',
    'Class Index': 'classes.md',
    'Class Hierarchy': 'hierarchy.md',
    'Class Members': 'class_members.md',
    'Class Member Functions': 'class_member_functions.md',
    'Class Member Variables': 'class_member_variables.md',
    'Class Member Typedefs': 'class_member_typedefs.md',
    'Class Member Enumerations': 'class_member_enums.md',
}

def generate_link(name, url) -> str:
    return '* [' + name + '](' + url + ')\n'

class Generator:
    def __init__(self, ignore_errors: bool = False, options: dict = {}):
        self.options = options

        on_undefined_class = Undefined
        if not ignore_errors:
            on_undefined_class = StrictUndefined

        try: 
            self.annotated_template = Template(ANNOTATED_TEMPLATE, undefined=on_undefined_class)
            self.member_template = Template(MEMBER_TEMPLATE, undefined=on_undefined_class)
            self.member_definition_template = Template(MEMBER_DEFINITION_TEMPLATE, undefined=on_undefined_class)
            self.member_table_template = Template(MEMBER_TABLE_TEMPLATE, undefined=on_undefined_class)
            self.namespaces_template = Template(NAMESPACES_TEMPLATE, undefined=on_undefined_class)
            self.classes_template = Template(CLASSES_TEMPLATE, undefined=on_undefined_class)
            self.hiearchy_template = Template(HIEARARCHY_TEMPLATE, undefined=on_undefined_class)
            self.index_template = Template(INDEX_TEMPLATE, undefined=on_undefined_class)
            self.modules_template = Template(MODULES_TEMPLATE, undefined=on_undefined_class)
            self.files_template = Template(FILES_TEMPLATE, undefined=on_undefined_class)
            self.programlisting_template = Template(PROGRAMLISTING_TEMPLATE, undefined=on_undefined_class)
            self.page_template = Template(PAGE_TEMPLATE, undefined=on_undefined_class)
            self.pages_template = Template(PAGES_TEMPLATE, undefined=on_undefined_class)
        except TemplateSyntaxError as e:
            raise Exception(str(e) + ' at line: ' + str(e.lineno))

    def _render(self, tmpl: Template, path: str, data: dict) -> str:
        try: 
            print('Generating', path)
            data.update(self.options)
            output = tmpl.render(data)

            with open(path, 'w', encoding='utf-8') as file:
                file.write(output) 
        except TemplateError as e:
            raise Exception(str(e))

    def _recursive_find(self, nodes: [Node], kind: Kind):
        ret = []
        for node in nodes:
            if node.kind == kind:
                ret.append(node)
            if node.kind.is_parent():
                ret.extend(self._recursive_find(node.children, kind))
        return ret

    def _recursive_find_with_parent(self, nodes: [Node], kinds: [Kind], parent_kinds: [Kind]):
        ret = []
        for node in nodes:
            if node.kind in kinds and node.parent is not None and node.parent.kind in parent_kinds:
                ret.append(node)
            if node.kind.is_parent() or node.kind.is_dir() or node.kind.is_file():
                ret.extend(self._recursive_find_with_parent(node.children, kinds, parent_kinds))
        return ret

    def annotated(self, output_dir: str, nodes: [Node]):
        path = os.path.join(output_dir, 'annotated.md')

        data = {
            'nodes': nodes
        }
        self._render(self.annotated_template, path, data) 

    def programlisting(self, output_dir: str, node: [Node]):
        path = os.path.join(output_dir, node.refid + '_source.md')

        data = {
            'node': node
        }
        self._render(self.programlisting_template, path, data) 

    def fileindex(self, output_dir: str, nodes: [Node]):
        path = os.path.join(output_dir, 'files.md')

        data = {
            'nodes': nodes
        }
        self._render(self.files_template, path, data) 

    def namespaces(self, output_dir: str, nodes: [Node]):
        path = os.path.join(output_dir, 'namespaces.md')

        data = {
            'nodes': nodes
        }
        self._render(self.namespaces_template, path, data)

    def page(self, output_dir: str, node: Node):
        path = os.path.join(output_dir, node.name + '.md')

        data = {
            'node': node
        }
        self._render(self.page_template, path, data)

    def pages(self, output_dir: str, nodes: [Node]):
        for node in nodes:
            self.page(output_dir, node)

    def relatedpages(self, output_dir: str, nodes: [Node]):
        path = os.path.join(output_dir, 'pages.md')

        data = {
            'nodes': nodes
        }
        self._render(self.pages_template, path, data)

    def classes(self, output_dir: str, nodes: [Node]):
        path = os.path.join(output_dir, 'classes.md')

        classes = self._recursive_find(nodes, Kind.CLASS)
        classes.extend(self._recursive_find(nodes, Kind.STRUCT))
        classes.extend(self._recursive_find(nodes, Kind.INTERFACE))
        dictionary = {}

        for letter in LETTERS:
            dictionary[letter] = []

        for klass in classes:
            dictionary[klass.name_short[0].lower()].append(klass)

        for letter in list(dictionary):
            if len(dictionary[letter]) == 0:
                del dictionary[letter]

        data = {
            'dictionary': dictionary
        }
        self._render(self.classes_template, path, data) 

    def _find_base_classes(self, nodes: [Node], derived: Node):
        ret = []
        for node in nodes:
            if isinstance(node, str):
                ret.append({
                    'refid': node, 
                    'derived': derived
                })
            elif node.kind.is_parent() and not node.kind.is_namespace():
                bases = node.base_classes
                if len(bases) == 0:
                    ret.append(node)
                else:
                    ret.extend(self._find_base_classes(bases, node))
        return ret

    def modules(self, output_dir: str, nodes: [Node]):
        path = os.path.join(output_dir, 'modules.md')

        data = {
            'nodes': nodes
        }
        self._render(self.modules_template, path, data) 

    def hierarchy(self, output_dir: str, nodes: [Node]):
        path = os.path.join(output_dir, 'hierarchy.md')

        classes = self._recursive_find(nodes, Kind.CLASS)
        classes.extend(self._recursive_find(nodes, Kind.STRUCT))
        classes.extend(self._recursive_find(nodes, Kind.INTERFACE))

        bases = self._find_base_classes(classes, None)
        deduplicated = {}

        for base in bases:
            if not isinstance(base, dict):
                deduplicated[base.refid] = base
                
        for base in bases:
            if isinstance(base, dict):
                if base['refid'] not in deduplicated:
                    deduplicated[base['refid']] = []
                deduplicated[base['refid']].append(base)

        deduplicated_arr = []
        for key, children in deduplicated.items():
            if isinstance(children, list):
                deduplicated_arr.append(DummyNode(
                    key,
                    list(map(lambda x: x['derived'], children)),
                    Kind.CLASS
                ))
            else:
                found: Node = None
                for klass in classes:
                    if klass.refid == key:
                        found = klass
                        break
                if found:
                    deduplicated_arr.append(found)

        data = {
            'classes': deduplicated_arr
        }
        self._render(self.hiearchy_template, path, data) 

    def member(self, output_dir: str, node: Node):
        path = os.path.join(output_dir, node.filename)

        data = {
            'node': node,
            'member_definition_template': self.member_definition_template,
            'member_table_template': self.member_table_template
        }
        self._render(self.member_template, path, data)

        if node.is_language or node.is_group or node.is_file or node.is_dir:
            self.members(output_dir, node.children)

    def file(self, output_dir: str, node: Node):
        path = os.path.join(output_dir, node.filename)

        data = {
            'node': node,
            'member_definition_template': self.member_definition_template,
            'member_table_template': self.member_table_template
        }
        self._render(self.member_template, path, data)

        if node.is_file and node.has_programlisting:
            self.programlisting(output_dir, node)

        if node.is_file or node.is_dir:
            self.files(output_dir, node.children)

    def members(self, output_dir: str, nodes: [Node]):
        for node in nodes:
            if node.is_parent or node.is_group or node.is_file or node.is_dir:
                self.member(output_dir, node)

    def files(self, output_dir: str, nodes: [Node]):
        for node in nodes:
            if node.is_file or node.is_dir:
                self.file(output_dir, node)

    def index(self, output_dir: str, nodes: [Node], kind_filters: Kind, kind_parents: [Kind], title: str):
        path = os.path.join(output_dir, title.lower().replace(' ', '_') + '.md')

        found_nodes = self._recursive_find_with_parent(nodes, kind_filters, kind_parents)
        dictionary = {}

        # Populate initial dictionary
        for letter in LETTERS:
            dictionary[letter] = []

        # Sort items into the dictionary
        for found in found_nodes:
            dictionary[found.name_tokens[-1][0].lower()].append(found)

        # Delete unused letters
        for letter in list(dictionary):
            if len(dictionary[letter]) == 0:
                del dictionary[letter]

        # Sort items if they have the same name
        sorted_dictionary = {}
        for letter, items in dictionary.items():
            d = {}
            for item in items:
                # The name of the item is not yet in the dictionary
                if item.name_short not in d:
                    d[item.name_short] = [item.parent]

                # If the key is already in the dictionary,
                # make sure there are no duplicates.
                # For example an overloaded constructor or function!
                # Only allow distinct parents
                else:
                    found = False
                    for test in d[item.name_short]:
                        if test.refid == item.parent.refid:
                            found = True
                            break
                    if not found:
                        d[item.name_short].append(item.parent)

            sorted_dictionary[letter] = d

        data = {
            'title': title,
            'dictionary': sorted_dictionary
        }
        self._render(self.index_template, path, data)

    def _generate_recursive(self, f: TextIO, node: Node, level: int, diff: str):
        if node.kind.is_parent():
            f.write(' ' * level + generate_link(node.kind.value + ' ' + node.name, diff + '/' + node.refid + '.md'))
            for child in node.children:
                self._generate_recursive(f, child, level + 2, diff)

    def _generate_recursive_files(self, f: TextIO, node: Node, level: int, diff: str):
        if node.kind.is_file() or node.kind.is_dir():
            f.write(' ' * level + generate_link(node.name, diff + '/' + node.refid + '.md'))
            if node.kind.is_file():
                f.write(' ' * level + generate_link(node.name + ' source', diff + '/' + node.refid + '_source.md'))
            for child in node.children:
                self._generate_recursive_files(f, child, level + 2, diff)

    def _generate_recursive_groups(self, f: TextIO, node: Node, level: int, diff: str):
        if node.kind.is_group():
            f.write(' ' * level + generate_link(node.title, diff + '/' + node.refid + '.md'))
            for child in node.children:
                self._generate_recursive_groups(f, child, level + 2, diff)     

    def _generate_recursive_pages(self, f: TextIO, node: Node, level: int, diff: str):
        if node.kind.is_page():
            f.write(' ' * level + generate_link(node.title, diff + '/' + node.refid + '.md'))
            for child in node.children:
                self._generate_recursive_pages(f, child, level + 2, diff)     

    def summary(self, output_dir: str, summary_file: str, nodes: [Node], modules: [Node], files: [Node], pages: [Node]):
        print('Modifying', summary_file)
        summaryDir = os.path.dirname(os.path.abspath(summary_file))
        output_path = os.path.abspath(output_dir)
        diff = output_path[len(summaryDir)+1:].replace('\\', '/')
        link = diff + '/index.md'

        content = []
        with open(summary_file, 'r') as f:
            content = f.readlines()

        start = None
        offset = 0
        end = None
        for i in range(0, len(content)):
            line = content[i]
            if start is None and re.search(re.escape(link), line):
                m = re.search('\\* \\[', line)
                if m is not None:
                    start = m.start()
                    start = i
                continue
            
            if start is not None and end is None:
                if not line.startswith(' ' * (offset + 2)):
                    end = i

        if start is None:
            print('WARNING: Could not generate summary! Unable to find \"* [...](' + link + ')\" in SUMMARY.md')
            return

        if end is None:
            end = len(content)

        with open(summary_file, 'w+') as f:
            # Write first part of the file
            for i in range(0, start+1):
                f.write(content[i])

            f.write(' ' * (offset+2) + generate_link('Related Pages', diff + '/' + 'pages.md'))
            for node in pages:
                self._generate_recursive_pages(f, node, offset + 4, diff)

            f.write(' ' * (offset+2) + generate_link('Modules', diff + '/' + 'modules.md'))
            for node in modules:
                self._generate_recursive_groups(f, node, offset + 4, diff)

            f.write(' ' * (offset+2) + generate_link('Class List', diff + '/' + 'annotated.md'))
            for node in nodes:
                self._generate_recursive(f, node, offset + 4, diff)  

            for key, val in ADDITIONAL_FILES.items():
                f.write(' ' * (offset+2) + generate_link(key, diff + '/' + val))

            f.write(' ' * (offset+2) + generate_link('Files', diff + '/' + 'files.md'))
            for node in files:
                self._generate_recursive_files(f, node, offset + 4, diff)    

            f.write(' ' * (offset+2) + generate_link('File Variables', diff + '/' + 'variables.md'))
            f.write(' ' * (offset+2) + generate_link('File Functions', diff + '/' + 'functions.md'))
            f.write(' ' * (offset+2) + generate_link('File Macros', diff + '/' + 'macros.md'))

            # Write second part of the file
            for i in range(end, len(content)):
                f.write(content[i])
