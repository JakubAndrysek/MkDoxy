# Advanced usage





## Disabling the plugin
You can use the `enabled` option to optionally disable this plugin. A possible use case is local development where you might want faster build times.

```yaml hl_lines="3"
plugins:
  - mkdoxy:
      enabled: !ENV [ENABLE_MKDOXY, True]
      ...
```

This will disable the plugin if the `ENABLE_MKDOXY` environment variable is not set or is set to `False`.
Inspirated by [mkdocs-simple-hooks](https://github.com/aklajnert/mkdocs-simple-hooks)

```bash
export ENABLE_MKDOXY=False
mkdocs serve
```

## Configure custom Doxygen binary

By default, the plugin will use the `doxygen` binary from the system path. You can configure a custom binary using the `doxygen-bin-path` option.
If `doxygen-bin-path` is not found, the plugin will raise DoxygenBinPathNotValid exception.

- addad by [thb-sb](https://github.com/thb-sb)

```yaml hl_lines="3"
plugins:
  - mkdoxy:
      doxygen-bin-path: /path/to/doxygen
      ...
```

## Configure custom Doxygen configuration file
If you want to use a standard Doxygen configuration file, you can specify the path to the file using the `doxygen-config` option in the plugin configuration.

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
