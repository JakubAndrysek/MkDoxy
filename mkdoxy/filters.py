import re


PLAIN_CODE_BLOCK = re.compile(r'```(\n.*?\n)```', re.DOTALL)


def use_code_language(value, code_language: str|None):
    """! Jinja2 filter to apply a code language to all plain code blocks
    @details
    @param value: the value to apply the filter to.
    @param code_language (str|None): the code language to apply.
    @return: The filtered value.
    """
    if not code_language:
        return value

    return re.sub(
        PLAIN_CODE_BLOCK,
        lambda m: f'```{code_language}{m[1]}```',
        str(value)
    )
    
