# Snippets - Functions

## `::: doxy.<project>.function`

This tag generates full function documentation.

| Parameter | Description               | Required |
|-----------|---------------------------|----------|
| `name`    | The name of the function. | Yes      |


=== "Tag usage"
    ```yaml
    ::: doxy.animal.function
        name: int main(int argc, char const *argv[])
    ```
=== "Tag result"
::: doxy.animal.function
name: int main(int argc, char const *argv[])
indent_level: 4


## `::: doxy.<project>.function` error message

=== "Tag usage"
    ```yaml
    ::: doxy.animal.function
        name: mEin
    ```
=== "Tag result"
::: doxy.animal.function
name: mEin
indent_level: 4
