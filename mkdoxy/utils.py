import logging
import re

from mkdocs.config import Config
from ruamel.yaml import YAML

log: logging.Logger = logging.getLogger("mkdocs")


regex = r"(-{3}|\.{3})\n(?P<meta>([\S\s])*)\n(-{3}|\.{3})\n(?P<template>([\S\s])*)"

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


def contains(a, pos, b):
	ai = pos
	bi = 0
	if len(b) > len(a) - ai:
		return False
	while bi < len(b):
		if a[ai] != b[bi]:
			return False
		ai += 1
		bi += 1
	return True


def split_safe(s: str, delim: str) -> [str]:
	tokens = []
	i = 0
	last = 0
	inside = 0
	while i < len(s):
		c = s[i]
		if i == len(s) - 1:
			tokens.append(s[last:i + 1])
		if c in ['<', '[', '{', '(']:
			inside += 1
			i += 1
			continue
		if c in ['>', ']', '}', ')']:
			inside -= 1
			i += 1
			continue
		if inside > 0:
			i += 1
			continue
		if contains(s, i, delim):
			tokens.append(s[last:i])
			i += 2
			last = i
		i += 1
	return tokens


def parseTemplateFile(templateFile: str):
	match = re.match(regex, templateFile, re.MULTILINE)
	if match:
		template = match["template"]
		meta = match["meta"]
		yaml = YAML(typ='safe')
		metaData = yaml.load(meta)
		# yaml.dump(metaData, sys.stdout)
		return template, metaData
	return templateFile, {}


def merge_two_dicts(base, new):
	"https://stackoverflow.com/a/26853961"
	result = base.copy()  # start with keys and values of x
	result.update(new)  # modifies z with keys and values of y
	return result

# def recursive_find(nodes: [Node], kind: Kind):
def recursive_find(nodes, kind):
	ret = []
	for node in nodes:
		if node.kind == kind:
			ret.append(node)
		if node.kind.is_parent():
			ret.extend(recursive_find(node.children, kind))
	return ret

# def recursive_find_with_parent(nodes: [Node], kinds: [Kind], parent_kinds: [Kind]):
def recursive_find_with_parent(nodes, kinds, parent_kinds):
	ret = []
	for node in nodes:
		if node.kind in kinds and node.parent is not None and node.parent.kind in parent_kinds:
			ret.append(node)
		if node.kind.is_parent() or node.kind.is_dir() or node.kind.is_file():
			ret.extend(recursive_find_with_parent(node.children, kinds, parent_kinds))
	return ret

def check_enabled_markdown_extensions(config: Config, mkdoxyConfig: Config) -> None:
	# sourcery skip: merge-nested-ifs
	"""
	Checks if the required markdown extensions are enabled.
	:param config: The MkDocs config.
	"""
	# enabled_extensions = config['markdown_extensions']
	# if mkdoxyConfig.get("emojis-enabled", False):
	# 	if 'pymdownx.emoji' not in enabled_extensions:
	# 		log.warning("The 'pymdownx.emoji' extension is not enabled. Some emojis may not be rendered correctly. https://squidfunk.github.io/mkdocs-material/reference/icons-emojis/#configuration")