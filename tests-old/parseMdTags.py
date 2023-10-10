import re
import sys
import yaml


def readFile(filename: str) -> str:
    file = open(filename, "r")
    return file.read()


if __name__ == "__main__":
    md = readFile("files/special/findTags.md")

    # regex = r"(?s)(^::: doxy.(?P<title>[a-zA-Z.-_]+))\n(?P<yaml>.*?)(?:(?:\r*\n){2})"
    # regex = r"(?s)(^::: doxy.(?P<title>[a-zA-Z.-_]+))\n(?P<yaml>.*?)(?:((?:\r*\n){2})|(?::::))"
    # regex = r"(?s)(?<!`\n)(^::: doxy.(?P<title>[a-zA-Z.-_]+))\n(?P<yaml>.*?)(?:((?:\r*\n){2})|(?=:::))"
    # regex = r"(?s)(?<!`\n)(^::: doxy.(?P<title>[a-zA-Z.-_]+))\n(?P<yaml>.*?)(?:((?:\r*\n)(?=\n))|(?=:::))"
    regex = r"(?s)(?<!```yaml\n)(^::: doxy.(?P<title>[a-zA-Z.-_]+))\n(?P<yaml>.*?)(?:(?:(?:\r*\n)(?=\n))|(?=:::)|(?=`))"

    matches = re.finditer(regex, md, re.MULTILINE)

    for match in matches:
        title = match.group("title")
        print(f"Title: {title}")

        yamlRaw = match.group("yaml")
        if yamlRaw:
            try:
                config = yaml.safe_load(yamlRaw)
                yaml.safe_dump(config, sys.stdout)
            except yaml.YAMLError as e:
                print(e)
        print()
