# MkDoxy

**[MkDoxy](https://mkdoxy.kubaandrysek.cz/)** plugin for **[MkDocs](https://www.mkdocs.org/)** generates API documentation based on **[Doxygen](https://www.doxygen.nl)** comments and **[code snippets](/intro)** in your markdown files.

<p align="center">
<a href="https://hits.seeyoufarm.com"><img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FJakubAndrysek%2FMkDoxy&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=true"/></a>
<a href="https://github.com/JakubAndrysek/MkDoxy/blob/main/LICENSE" target="_blank"><img src="https://img.shields.io/github/license/JakubAndrysek/MkDoxy?style=flat-square"></a>
<a href="https://github.com/JakubAndrysek/MkDoxy/releases" target="_blank"><img src="https://img.shields.io/github/v/release/JakubAndrysek/MkDoxy?style=flat-square"></a>
<a href="https://github.com/JakubAndrysek/MkDoxy/stargazers" target="_blank"><img src="https://img.shields.io/github/stars/JakubAndrysek/MkDoxy?style=flat-square"></a>
<a href="https://github.com/JakubAndrysek/MkDoxy/forks" target="_blank"><img src="https://img.shields.io/github/forks/JakubAndrysek/MkDoxy?style=flat-square"></a>
<a href="https://github.com/JakubAndrysek/MkDoxy/issues" target="_blank"><img src="https://img.shields.io/github/issues/JakubAndrysek/MkDoxy?style=flat-square"></a>
<a href="https://github.com/JakubAndrysek/MkDoxy/discussions" target="_blank"><img src="https://img.shields.io/github/discussions/JakubAndrysek/MkDoxy?style=flat-square"></a>
<a href="https://www.pepy.tech/projects/mkdoxy" target="_blank"><img src="https://static.pepy.tech/badge/mkdoxy"></a>
</p>

> **Warning**
> **Extension is in development**, and a few features are not working properly.
> More information in [Discussions](https://github.com/JakubAndrysek/MkDoxy/discussions) and [Issues](https://github.com/JakubAndrysek/MkDoxy/issues) pages.

---

## [:material-home-edit: Online Demo](https://jakubandrysek.github.io/MkDoxy-demo/) and [:simple-github: Demo source-code ](https://github.com/JakubAndrysek/MkDoxy-demo)

---

**[Feature List](#feature-list)** - **[Installation](#installation)** - **[Quick start](#quick-start)**

## Feature List
- **[Easy to use](#quick-start):**: Just add `mkdoxy` to your `mkdocs.yml` and configure the path to your source code.
- **[Code snippets](./snippets/index.md)**: Generate code snippets in place of your standard Markdown documentation.
- **[Multiple projects](./usage/index.md#multiple-projects)**: Support for multiple projects in one documentation (e.g. C++ and Python).
- **[Multiple source directories](./usage/index.md#multiple-source-directories)**: Configure multiple source directories in one project.
- **[Custom Jinja templates](./usage/index.md#custom-jinja-templates)**: Define custom Jinja templates for rendering Doxygen documentation.
- **[Custom Doxygen configuration](./usage/index.md#custom-doxygen-configuration)**: Specify custom Doxygen configuration for each project.
- **[Remote Git sources](#project-configuration-options)**: Clone source code directly from a Git repository (`git-url`, `git-branch`).
- **[Navigation injection](#navigation-injection)**: Inject generated API pages into an existing `nav` section (`parent-nav-section`).
- **[Custom landing pages](#navigation-injection)**: Replace a navigation entry with a custom landing page (`landing-page`, `landing-page-replaces`).

## Installation
Install the plugin using pip from [PyPI](https://pypi.org/project/mkdoxy/):

```bash
pip install mkdoxy
```
Development version with all dependencies:
```bash
python -m pip install mkdoxy ".[dev]"
```

Install from source:
```bash
pip install git+https://github.com/JakubAndrysek/MkDoxy.git
```

## Quick start

`mkdocs.yml`:
```yaml
site_name: "My MkDoxy documentation"

theme:
  name: material

plugins:
  - search
  - mkdoxy:
      projects:
        myProjectCpp: # name of project must be alphanumeric + numbers (without spaces)
          src-dirs: path/to/src/project1 # path to source code (support multiple paths separated by space) => INPUT
          full-doc: True # if you want to generate full documentation
          doxy-cfg: # standard doxygen configuration (key: value)
            FILE_PATTERNS: "*.cpp *.h*" # specify file patterns to filter out
            RECURSIVE: True # recursive search in source directories
```

## Project Configuration Options

Each project under `projects` supports the following options:

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `src-dirs` | str | – | Path(s) to source code, separated by spaces. |
| `full-doc` | bool | `True` | Generate full API documentation. |
| `debug` | bool | `False` | Enable debug logging for this project. |
| `api-path` | str | `.` | Sub-path under which the generated API is placed. |
| `doxy-cfg` | dict | `{}` | Extra Doxygen configuration (`key: value`). |
| `doxy-cfg-file` | str | `""` | Path to an existing Doxygen config file. |
| `template-dir` | str | `""` | Directory with custom Jinja templates. |
| `git-url` | str | `""` | Clone source code from this Git repository instead of a local path. |
| `git-branch` | str | `main` | Branch to clone when `git-url` is set. |
| `parent-nav-section` | str | `""` | Inject generated pages under this `nav` section (see below). |
| `landing-page` | str | `""` | Path (relative to `docs/`) used as the project's landing page. |
| `landing-page-replaces` | str | `""` | Existing `nav` entry (within `parent-nav-section`) to replace with the landing page. |

### Remote Git sources

Instead of a local `src-dirs`, a project can be cloned from Git:

```yaml
plugins:
  - mkdoxy:
      git-recursive: false # clone submodules recursively (global option)
      projects:
        myApi:
          git-url: https://example.com/group/my-api.git
          git-branch: development
          doxy-cfg:
            GENERATE_XML: YES
```

### Navigation injection

Generated API pages can be injected into an existing `nav` section using
`parent-nav-section`. The value is a `::`-separated path to a (possibly nested)
section in your `nav`.

```yaml
# mkdocs.yml (nav)
nav:
  - APIs:
    - my-api:
      - 'apis/my_api/index.md'

# plugin config
plugins:
  - mkdoxy:
      projects:
        my-api:
          git-url: https://example.com/group/my-api.git
          parent-nav-section: 'APIs::my-api'
          landing-page: 'apis/my_api/index.md'
          landing-page-replaces: 'apis/my_api/index.md'
```

How it works:

- `parent-nav-section`: all generated pages are appended under this section.
- `landing-page-replaces`: the entry with this path (searched **only** within
  `parent-nav-section`) is replaced, keeping its original title. Only that one
  occurrence is touched, so other references to the same file elsewhere in the
  `nav` stay intact.
- `landing-page`: the path used as replacement. If omitted, MkDoxy falls back to
  the Doxygen mainpage (`indexpage.md`) or the first related page in `pages.md`.

If `landing-page-replaces` is not set, generated pages (including the landing
page) are simply appended to the section as usual.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you want to change.

## Do You Enjoy MkDoxy or Does It Save You Time?
Then definitely consider:

- supporting me on GitHub Sponsors: [![](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/jakubandrysek)

## License

This project is licensed under the terms of the [MIT license](https://github.com/JakubAndrysek/MkDoxy/blob/main/LICENSE)
