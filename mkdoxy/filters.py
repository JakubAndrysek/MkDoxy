import re
from typing import Optional

PLAIN_CODE_BLOCK = re.compile(r"```(\n.*?\n)```", re.DOTALL)


def use_code_language(value, code_language: Optional[str]):
    """! Jinja2 filter to apply a code language to all plain code blocks
    @details
    @param value: the value to apply the filter to.
    @param code_language (str|None): the code language to apply.
    @return: The filtered value.
    """
    return (
        re.sub(
            PLAIN_CODE_BLOCK,
            lambda m: f"```{code_language}{m[1]}```",
            str(value),
        )
        if code_language
        else value
    )
