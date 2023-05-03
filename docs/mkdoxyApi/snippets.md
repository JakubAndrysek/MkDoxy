# Snippets for the Doxygen API documentation

Writing documentation snippets is one of the most important parts of the mkdoxy project.
Uou can write standard markdown documentation and using the `::: doxy` tags embed your code snippets just in the right place.
Using this tags is inspired from the [mkdocstrings](https://mkdocstrings.github.io/) project.

## Using the tags
Code tags consist of three parts: the tag **keyword**, the **project name** and the **tag name** separated by the `.` character.
The parameters of the tag are passed as a YAML object (key:value) in the next line indented by 4 spaces or a tab.

=== "Tag structure"

	```yaml
	::: doxy.<project name>.<tag name>
		<key>:<value>
		<key>:<value>
	```

=== "Tag example"

	```yaml
	::: doxy.mkdoxyApi.class.method
		name: mkdoxy::cache::Cache
		method: get
	```


- `::: doxy` - the tag keyword is always same
- `<project name>` - the name of the project. This is configured in the `mkdoxy.yml` file.
- `<tag name>` - the name of the tag. List of available tags can be found in LINK TO TAGS.
  - `<key>:<value>` - the parameters of the tag. The parameters are passed as a YAML object (key:value) each `<tag name>` has its own set of parameters.


## Available tags

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


### `::: doxy.<project>.namespace.list`
This tag generates a list of all namespaces in the project.

=== "Tag usage"
    ```yaml
    ::: doxy.mkdoxyApi.namespace.list
    ```

=== "Tag result"
::: doxy.mkdoxyApi.namespace.list
indent_level: 4

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