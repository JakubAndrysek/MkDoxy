# Usage

MkDoxy creates API documentation based on Doxygen comments and code snippets in your markdown files.

```yaml
site_name: "My documentation"

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

## How does it work
1. MkDoxy runs Doxygen to generate XML files from your source code (this is executed only if the source code has changed).
2. MkDoxy parses the XML files and creates a recursive structure of each project.
3. Plugin generates markdown files from the recursive structure based on Jinja templates.
4. Find snippets tags in the markdown files and replace them with the configured code snippets.
5. Plugin includes the generated markdown files in the final documentation.
6. MkDocs generates the final documentation.

## Multiple projects

MkDoxy supports multiple projects in one repository.
Each project must have its own configuration.
The configuration is specified in the `projects` section of the MkDoxy configuration.
The name of the project must be alphanumeric + numbers (without spaces).
The name of the project is used to identify the project in the snippet tags.

??? abstract "Configure multiple projects"
    ```yaml hl_lines="4-5 7-8 10-11"
    plugins:
      - mkdoxy:
          projects:
            apiProject1: # name of project must be alphanumeric + numbers (without spaces)
              src-dirs: path/to/src/project1
              ...
            apiProject2:
              src-dirs: path/to/src/project2
              ...
            predefinedProject3:
                src-dirs: path/to/src/project3
                ...
    ```

## Custom Jinja templates

Custom templates can be used to change the appearance of the generated documentation.
Each custom template file will replace the default template file.
Custom templates have to end with `.jinja2`, `.j2`, or `.jinja` extension.
So you do not have to create a custom template for the whole documentation, but only for the parts you want to change.

??? abstract "Custom Jinja templates"
    ```yaml hl_lines="6"
    plugins:
      - mkdoxy:
          projects:
            projectWithCustomTemplate:
                src-dirs: path/to/src/project1
                template-dir: path/to/userDefined/templates # optional (default is mkdoxy/templates) - custom template will replace default template
    ```


## Custom Doxygen configuration

MkDoxy supports custom Doxygen configuration for each project.
The configuration is specified in the `doxy-cfg` section of the project configuration.
The configuration is passed to Doxygen as a string.
The configuration is merged with the default configuration.
??? info "Default Doxygen configuration"
    ```py
    "INPUT": self.doxygenSource, # path to source code
    "OUTPUT_DIRECTORY": self.tempDoxyFolder, # path to temporary folder
    "DOXYFILE_ENCODING": "UTF-8", # encoding of doxygen configuration file
    "GENERATE_XML": "YES", # generate XML files (required by mkdoxy)
    "RECURSIVE": "YES", # recursive search for source files
    "SHOW_NAMESPACES": "YES", # show namespaces in documentation
    "GENERATE_HTML": "NO", # do not generate HTML files (mkdoxy generates documentation from XML files)
    "GENERATE_LATEX": "NO", # do not generate LaTeX files
    ```


Doxygen configuration options: [www.doxygen.nl/manual/config.html](https://www.doxygen.nl/manual/config.html)

??? abstract "Custom Doxygen configuration - override default configuration"
    ```yaml hl_lines="7-13"
    plugins:
      - mkdoxy:
          projects:
            pythonProject:
              src-dirs: path/to/src/pythonProject
              full-doc: True
              doxy-cfg:
                FILE_PATTERNS: "*.py"
                EXAMPLE_PATH: ""
                RECURSIVE: True
                OPTIMIZE_OUTPUT_JAVA: True
                JAVADOC_AUTOBRIEF: True
                EXTRACT_ALL: True
                ...
    ```

## Configure custom Doxygen configuration file
If you want to use a standard `Doxygen` configuration file, you can specify the path to the file using the `doxygen-config` option in the plugin configuration.

??? abstract "Add custom Doxygen configuration file"
    ```yaml hl_lines="6"
    plugins:
      - mkdoxy:
          projects:
            myProjectCpp:
              src-dirs: ...
              doxy-cfg-file: path/to/Doxyfile  # relative path to the Doxygen configuration file (relative to the mkdocs.yml file)
              doxy-cfg:       # standard doxygen configuration (key: value)
                FILE_PATTERNS: ... # other configuration options - merge (this will override the configuration from the Doxyfile)
    ```

    ??? example "How is it implemented?"

::: doxy.mkdoxyApi.code
file: doxyrun.py
start: 64
end: 115
indent_level: 8




## Advanced configuration

??? abstract "mkdocs.yml configuration"
    ```yaml
    plugins:
      - mkdoxy:
          projects:
            apiProject1: # name of project must be alphanumeric + numbers (without spaces)
              src-dirs: path/to/src/project1
              full-doc: True
              doxy-cfg:
                FILE_PATTERNS: "*.cpp *.h*"
                EXAMPLE_PATH: examples
                RECURSIVE: True
            apiProject2:
              src-dirs: path/to/src/project2
              full-doc: True
              template-dir: path/to/userDefined/templates # optional (default is mkdoxy/templates) - custom template will replace default template
              # Example of custom template: https://mkdoxy-demo.kubaandrysek.cz/esp/annotated/
              doxy-cfg:
                FILE_PATTERNS: "*.py"
                EXAMPLE_PATH: ""
                RECURSIVE: True
                OPTIMIZE_OUTPUT_JAVA: True
                JAVADOC_AUTOBRIEF: True
                EXTRACT_ALL: True
            predefinedProject3:
              src-dirs: path/to/src/project3
              full-doc: False
              doxy-cfg:
                PREDEFINED: __cplusplus # example there: https://github.com/kuba2k2/libretuya/blob/master/mkdocs.yml
                CASE_SENSE_NAMES: NO
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
