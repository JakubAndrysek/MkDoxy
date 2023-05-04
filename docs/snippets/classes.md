# Snippets - Classes

### `::: doxy.<project>.class`
This tag generates full class documentation.

| Parameter | Description            | Required |
|-----------|------------------------|----------|
| `name`    | The name of the class. | Yes      |


=== "Tag usage"
    ```yaml
    ::: doxy.mkdoxyApi.class.method
    name: mkdoxy::cache::Cache
    ```

=== "Tag result"
::: doxy.mkdoxyApi.class
name: mkdoxy::cache::Cache
indent_level: 4


### `::: doxy.<project>.class.method`
This tag generates documentation for a specific method of a class.

| Parameter | Description             | Required |
|-----------|-------------------------|----------|
| `name`    | The name of the class.  | Yes      |
| `method`  | The name of the method. | Yes      |

=== "Tag usage"
    ```yaml
    ::: doxy.mkdoxyApi.class.method
    name: mkdoxy::cache::Cache
    method: get
    ```

=== "Tag result"
::: doxy.mkdoxyApi.class.method
name: mkdoxy::cache::Cache
method: get
indent_level: 4



### `::: doxy.<project>.class.list`
This tag generates a list of all classes in the project.

There are no parameters for this tag.

=== "Tag usage"
```yaml
::: doxy.mkdoxyApi.class.list
```

=== "Tag result"
::: doxy.mkdoxyApi.class.list
indent_level: 4





### `::: doxy.<project>.class.hierarchy`
This tag generates a class hierarchy diagram.

There are no parameters for this tag.

=== "Tag usage"
```yaml
::: doxy.mkdoxyApi.class.hierarchy
```

=== "Tag result"
::: doxy.mkdoxyApi.class.hierarchy
indent_level: 4