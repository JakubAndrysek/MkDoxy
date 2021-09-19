# CONFIG = {
# 	"header": False,
# 	"breadcrumbs": False
# }

TEMPLATE = """
# {{node.kind.value|title}} {{node.name_long}}

[**File List**]({{link_prefix}}files.md)
{%- for child in node.parents -%}
{{'**>**'|indent(1, true)}} [**{{child.name_long if node.is_group else child.name_short}}**]({{child.url}})
{%- endfor %}

[Go to the documentation of this file.]({{node.url}}) 

{{node.programlisting}}
"""

# TEMPLATE = """
# {% if config.get('implements') -%}
# # {{node.kind.value|title}} {{node.name_long}}
# {%- endif %}
#
# {% if config.get('implements') -%}
# [**File List**]({{link_prefix}}files.md)
# {%- for child in node.parents -%}
# {{'**>**'|indent(1, true)}} [**{{child.name_long if node.is_group else child.name_short}}**]({{child.url}})
# {%- endfor %}
# {%- endif %}
#
# {% if config.get('doc') -%}
# [Go to the documentation of this file.]({{node.url}})
# {%- endif %}
#
# {{node.programlisting}}
# """
