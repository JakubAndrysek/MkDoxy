# Usage

MkDoxy creates API documentation based on Doxygen comments and code snippets in your markdown files.

## How does it work
1. MkDoxy runs Doxygen to generate XML files from your source code (this is executed only if the source code has changed).
2. MkDoxy parses the XML files and creates a recursive structure of each project.
3. Plugin generates markdown files from the recursive structure based on Jinja templates.
4. Find snippets tags in the markdown files and replace them with the configured code snippets.
5. Plugin includes the generated markdown files in the final documentation.
6. MkDocs generates the final documentation.

## Advanced usage


## Multiple projects

## Multiple source directories

## Custom Jinja templates

## Custom Doxygen configuration


### Advanced configuration

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

