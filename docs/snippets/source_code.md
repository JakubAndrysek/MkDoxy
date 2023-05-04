# Snippets - Source code

### `::: doxy.<project>.code`
This tag generates a code snippet from a file.

| Parameter | Description                               | Required |
|-----------|-------------------------------------------|----------|
| `file`    | The name of the file.                     | Yes      |
| `start`   | The line number where the snippet starts. | No       |
| `end`     | The line number where the snippet ends.   | No       |

=== "Tag usage"
    ```yaml
    ::: doxy.mkdoxyApi.code
    file: cache.py
    start: 8
    end: 13
    ```

=== "Tag result"
::: doxy.mkdoxyApi.code
file: cache.py
start: 8
end: 13
indent_level: 4