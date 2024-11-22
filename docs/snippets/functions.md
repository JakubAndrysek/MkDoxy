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

## `::: doxy.<project>.namespace.function`

This tag generates full function documentation.

| Parameter   | Description               | Required |
|-------------|---------------------------|----------|
| `namespace` | The name of the amespace. | Yes      |
| `name`      | The name of the function. | Yes      |


=== "Tag usage"
    ```yaml
    ::: doxy.animal.namespace.function
        namespace: example
        name: void some_namespace_function(Animal* animal)
    ```
=== "Tag result"
::: doxy.animal.namespace.function
namespace: example
name: void some_namespace_function(Animal* animal)
indent_level: 4


## `::: doxy.<project>.function` error message

=== "Tag usage"
    ```yaml
    ::: doxy.animal.namespace.function
        namespace: example
        name: void no_function()
    ```
=== "Tag result"
::: doxy.animal.function
namespace: example
name: void no_function()
indent_level: 4
