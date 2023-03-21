# MkDoxy

## MkDoxy → MkDocs + Doxygen = easy documentation generator with code snippets


<p align="center">
<a href="https://hits.seeyoufarm.com"><img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FJakubAndrysek%2FMkDoxy&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=true"/></a>
<img src="https://img.shields.io/github/license/JakubAndrysek/MkDoxy?style=flat-square">
</p>


> **Warning**
> **Extension is in development** and few features are not working properly. 
> More information in [Known issues](#known-issues) section and [Issues](https://github.com/JakubAndrysek/MkDoxy/issues) page.

#### [MkDoxy](https://github.com/JakubAndrysek/MkDoxy) is based on  [matusnovak/doxybook](https://matusnovak.github.io/doxybook)

This python tool is extension for MkDocs. Extension will take your programme source code and runs Doxygen.
Then converts exported XML into markdown and create new folder with full generated documentation.
Next usage is by snippets inside documentation markdown.

## [Online Demo](https://jakubandrysek.github.io/MkDoxy-demo/) and [Demo Source](https://github.com/JakubAndrysek/MkDoxy-demo)


![Basic-implementation](https://github.com/JakubAndrysek/MkDoxy/raw/main/docs/media/Basic-implementation.png)

## Requirements

- python 3.8 or newer → `sudo apt install python3`
- Pip → `sudo apt install python3-pip`
- Doxygen → `sudo apt install doxygen`
- Git → `sudo apt install git` (optional)

## Installation

**Install using Python Pip: <https://pypi.org/project/MkDoxy/>**

```bash
pip install mkdoxy
```

**Or installation from source:**

```bash
git clone https://github.com/JakubAndrysek/MkDoxy.git
cd mkdoxy
python setup.py install # for normal usage
pip install -e . # for development (source code changes are applied immediately)
```

## Example usage

Set `[PROJECT]` according to your project names configured in `mkdocs.yml`.

```bash

1. Generate class with name `rb::MotorChangeBuilder`

```yaml
::: doxy.[PROJECT].Class
  name: rb::MotorChangeBuilder
```

2. Generate method `brake (MotorId id, uint16_t brakingPower)` from class with name `rb::MotorChangeBuilderA`

```yaml
::: doxy.[PROJECT].Class.Method
  name: rb::MotorChangeBuilder
  method: brake (MotorId id, uint16_t brakingPower)
```

3. Generate function with name `readUltra (bool async)`

```yaml
::: doxy.[PROJECT].Function
  name: readUltra (bool async)
```

4. Generate code snippet from file `RBCXLeds.cpp`

```yaml
::: doxy.[PROJECT].Code
  file: RBCXLeds.cpp
  start: 21
  end: 35
```

### Mkdocs.yml

```yaml
plugins:
  - mkdoxy:
      projects:
        apiProject1:
          src-dirs: path/to/src/project1
          full-doc: True
          doxy-cfg:
            FILE_PATTERNS: "*.cpp *.h*"
            EXAMPLE_PATH: examples
            RECURSIVE: True
        apiProject2:
          src-dirs: path/to/src/project2
          full-doc: True
          doxy-cfg:
            FILE_PATTERNS: "*.py"
            EXAMPLE_PATH: ""
            RECURSIVE: True
            OPTIMIZE_OUTPUT_JAVA: True
            JAVADOC_AUTOBRIEF: True
            EXTRACT_ALL: True
...
nav:
  - Home: 'index.md'
  - API:
      - Project 1:
          - 'Links': 'apiProject1/links.md'
          - 'Classes':
              - 'Class List': 'apiProject1/annotated.md'
              - 'Class Index': 'apiProject1/classes.md'
              - 'Class Hierarchy': 'apiProject1/hierarchy.md'
              - 'Class Members': 'apiProject1/class_members.md'
              - 'Class Member Functions': 'apiProject1/class_member_functions.md'
              - 'Class Member Variables': 'apiProject1/class_member_variables.md'
              - 'Class Member Typedefs': 'apiProject1/class_member_typedefs.md'
              - 'Class Member Enumerations': 'apiProject1/class_member_enums.md'
          - 'Namespaces':
              - 'Namespace List': 'apiProject1/namespaces.md'
              - 'Namespace Members': 'apiProject1/namespace_members.md'
              - 'Namespace Member Functions': 'apiProject1/namespace_member_functions.md'
              - 'Namespace Member Variables': 'apiProject1/namespace_member_variables.md'
              - 'Namespace Member Typedefs': 'apiProject1/namespace_member_typedefs.md'
              - 'Namespace Member Enumerations': 'apiProject1/namespace_member_enums.md'
          - 'Functions': 'apiProject1/functions.md'
          - 'Variables': 'apiProject1/variables.md'
          - 'Macros': 'apiProject1/macros.md'
          - 'Files': 'apiProject1/files.md'
      - Project 2:
...

use_directory_urls: true # (optional) for better links without .html extension
```

## Known issues
1. **Doxygen** is not able to parse **Python** code. 
   - **Solution**: Use `OPTIMIZE_OUTPUT_JAVA: True` and `JAVADOC_AUTOBRIEF: True` in `doxy-cfg` section of `mkdocs.yml`.
2. `use_directory_urls: false` doesn't work with Mkdoxy. 
   - **Not fixed yet**


## License

```

MIT License

Copyright (c) 2021 Kuba Andrýsek

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```
