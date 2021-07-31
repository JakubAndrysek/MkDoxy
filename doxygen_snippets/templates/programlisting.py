TEMPLATE = """
# {{node.kind.value|title}} {{node.name_long}}

[**File List**]({{link_prefix}}files.md)
{%- for child in node.parents -%}
{{'**>**'|indent(1, true)}} [**{{child.name_long if node.is_group else child.name_short}}**]({{child.url}})
{%- endfor %}

[Go to the documentation of this file.]({{node.url}}) 

{{node.programlisting}}
"""
