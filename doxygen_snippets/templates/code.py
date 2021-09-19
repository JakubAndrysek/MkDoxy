CONFIG = {
	"header": False,
	"breadcrumbs": False,
	"source": False,
	"start": 1,
	"end": 0,
}

# TEMPLATE = """
# # {{node.kind.value|title}} {{node.name_long}}
#
# [**File List**]({{link_prefix}}files.md)
# {%- for child in node.parents -%}
# {{'**>**'|indent(1, true)}} [**{{child.name_long if node.is_group else child.name_short}}**]({{child.url}})
# {%- endfor %}
#
# [Go to the documentation of this file.]({{node.url}})
#
# {{node.programlisting}}
# """



TEMPLATE = """
{% if config.get('header') -%}
# {{node.kind.value|title}} {{node.name_long}}
{%- endif %}

{% if config.get('breadcrumbs') -%}
[**File List**]({{link_prefix}}files.md)
{%- for child in node.parents -%}
{{'**>**'|indent(1, true)}} [**{{child.name_long if node.is_group else child.name_short}}**]({{child.url}})
{%- endfor %}
{%- endif %}

{% if config.get('source') -%}
# [Go to the documentation of this file.]({{node.url}})
# {%- endif %}

{{code}}
"""
