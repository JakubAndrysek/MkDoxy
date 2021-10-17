TEMPLATE = """
# Related Pages

Here is a list of all related documentation pages:

{% for page in nodes -%}
* [*{{page.title}}*]({{link_prefix}}{{page.url}}) {{page.brief}}
{% endfor -%}
"""
