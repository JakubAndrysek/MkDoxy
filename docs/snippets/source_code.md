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
    ::: doxy.animal.code
    file: bird.h
    start: 4
    end: 20
    ```

=== "Tag result"
::: doxy.animal.code
file: bird.h
start: 4
end: 20
indent_level: 4

### `::: doxy.<project>.code` error message

=== "Tag usage"
    ```yaml
    ::: doxy.animal.code
        file: cat.h
    ```

=== "Tag result"
::: doxy.animal.code
    file: cat.h
    indent_level: 4
