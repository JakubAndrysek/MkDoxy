# This template is used inside of member.py
CONFIG = {
	"details": True,
	"implements": True
}

TEMPLATE = """
{% if target == 'gitbook' %}
### <a href="#{{node.anchor}}" id="{{node.anchor}}">{{node.kind.value}} {{node.name_long if node.is_group else node.name_short}} {{node.overload_suffix}}</a>
{% else %}
### {{node.kind.value}} {{node.name_long if node.is_group else node.name_short}} {{node.overload_suffix}}
{% endif %}

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
