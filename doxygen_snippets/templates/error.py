TEMPLATE = """
### Error: {{title}}
{%- if message %}
```
{{message}}
```
{%- endif %}
"""