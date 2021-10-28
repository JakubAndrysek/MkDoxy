# This template is used inside of member.py
CONFIG = {
	"brief": True,
	"details": True,
	"implements": True
}

TEMPLATE = """
### {{node.kind.value}} {{node.name_long if node.is_group else node.name_short}} {{node.overload_suffix}}

{% if config.get('brief') -%}
{% if node.has_brief -%}
{{node.brief + "\n"}}
{%- endif -%}
{%- endif -%}

```cpp
{{node.codeblock}}
```


{% if config.get('details') -%}
{% if node.has_details -%}
{{node.details}}
{%- endif -%}
{%- endif -%}

{% if config.get('implements') -%}
{% if node.reimplements %}
Implements [*{{node.reimplements.name_long}}*]({{node.reimplements.url}})
{% endif %}
{%- endif -%}

"""
