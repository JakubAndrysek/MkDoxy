import sys
import re
import yaml


text = """\
---
brief: True
details: True
implements: True
---

# {{node.kind.value|title}} {{node.name_long}}
{% if node.has_templateparams %}
**template &lt;{{node.templateparams}}&gt;**
{% endif %}


[**{{node.base_name}}**]({{node.base_url}})
{%- for parent in node.parents -%}
{{'**>**'|indent(1, true)}} [**{{parent.name_long if node.is_group else parent.name_short}}**]({{parent.url}})
{%- endfor %}

{% if node.is_file and node.has_programlisting -%}
[Go to the source code of this file.]({{node.url_source}})
{%- endif %}

{{node.brief}}
{%- if node.has_details -%}
[More...](#detailed-description)
{%- endif %}

{% if node.has_includes -%}
{%- for include in node.includes -%}
* `#include {{include}}`
{% endfor -%}
{%- endif %}
"""


text2 = """\
---
title: this is the title and it is compulsory
tags: this part is optional
something: this is not interesting, only 'title' and 'tags' is
---
some content
"""

regex = r"(-{3}|\.{3})\n(?P<meta>([\S\s])*)\n(-{3}|\.{3})\n(?P<template>([\S\s])*)"


match = re.match(regex, text2, re.MULTILINE)
match_meta = match["meta"]
config = yaml.safe_load(match_meta)
yaml.safe_dump(config, sys.stdout)
