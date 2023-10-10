# Snippets - Intelli sense and errors

## `::: doxy` tag

This tag shows all possible tags and their parameters.


=== "Tag usage"
    ```yaml
    ::: doxy
    ```
=== "Tag result"
::: doxy
indent_level: 4


## Error handling

When you configured the snippet incorrectly, MkDoxy show you an error message with a hint how to fix it.

=== "Tag usage"
    ```yaml
    ::: doxy.animal
    ```

=== "Tag result"
::: doxy.animal
indent_level: 4


## Incorrect arguments

When you configured the snippet with incorrect arguments, mkdoxyApi will show you an error message.


=== "Tag usage"
    ```yaml
    ::: doxy.animal.class.method
    name: cat
    ```

=== "Tag result"
::: doxy.animal.class
name: example::Cat
indent_level: 4


## Hints for parameters

=== "Tag usage"
    ```yaml
    ::: doxy.animal.class.method
    name: mkdoxy::cache::Cache
    ```
=== "Tag result"
::: doxy.animal.class.method
name: mkdoxy::cache::Cache
indent_level: 4
