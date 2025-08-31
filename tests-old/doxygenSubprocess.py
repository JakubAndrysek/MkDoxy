import shutil
from subprocess import PIPE, Popen

# Find doxygen executable
doxygen_path = shutil.which("doxygen")
if doxygen_path is None:
    raise FileNotFoundError("doxygen executable not found in PATH")

p = Popen(  # noqa: S603 - controlled test environment
    [doxygen_path, "-"],
    stdout=PIPE,
    stdin=PIPE,
    stderr=PIPE,
    shell=False
)

doxyfile_content = """
INPUT = files/src
OUTPUT_DIRECTORY = files/doxy2
DOXYFILE_ENCODING = UTF-8
GENERATE_XML = YES
RECURSIVE = YES
EXAMPLE_PATH = examples
SHOW_NAMESPACES = YES
GENERATE_HTML = NO
GENERATE_LATEX = NO
"""

stdout_data = p.communicate(
    doxyfile_content.encode("utf-8")
)[0].decode().strip()
print(stdout_data)
