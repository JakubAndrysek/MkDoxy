# Advanced usage





## Disabling the plugin
You can use the `enabled` option to optionally disable this plugin. A possible use case is local development where you might want faster build times.

```yaml
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

- addad by [thb-sb](https://github.com/thb-sb)

```yaml
plugins:
  - mkdoxy:
      doxygen-bin-path: /path/to/doxygen
      ...
```


## Add MkDoxy tag into the `<details>` tag
If you want to add MkDoxy tag into the `<details>` tag, you can use the `details` option.
In some cases, it might be tricky to configure indentation, so you can use the `indent_level` option to indent generated markdown block. 


<details>
<summary>my_class</summary>

::: doxy.animal.function
  name: int main(int argc, char const *argv[])
  indent_level: 4

</details>
