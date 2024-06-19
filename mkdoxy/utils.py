import logging
import re
import yaml

log: logging.Logger = logging.getLogger("mkdocs")

template_meta_regex = r"(-{3}|\.{3})\n(?P<meta>([\S\s])*)\n(-{3}|\.{3})\n(?P<template>([\S\s])*)"


# Credits: https://stackoverflow.com/a/1630350
def lookahead(iterable):
    """Pass through all values from the given iterable, augmented by the
    information if there are more values to come after the current one
    (True), or if it is the last value (False).
    """
    # Get an iterator and pull the first value.
    it = iter(iterable)
    last = next(it)
    # Run the iterator to exhaustion (starting from the second value).
    for val in it:
        # Report the *previous* value (more to come).
        yield last, True
        last = val
    # Report the last value.
    yield last, False


def load_template_meta(template_file_content: str) -> list:
    """! Load the template and metadata from the template file.
    @details
    @param template_file_content: (str) The template file content
    @return: (dict) The metadata
    """
    match = re.match(template_meta_regex, template_file_content, re.MULTILINE)
    return yaml.safe_load(match["meta"]) if match else []


def merge_two_dicts(base: dict, new: dict) -> dict:
    """https://stackoverflow.com/a/26853961"""
    result = base.copy()  # start with keys and values of x
    result.update(new)  # modifies z with keys and values of y
    return result
