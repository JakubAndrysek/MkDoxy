---
header: Snippets
---

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
