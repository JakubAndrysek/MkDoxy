import os
import subprocess
import shlex

import logging

logger = logging.getLogger("mkdocs")


class DoxygenRun:
    def __init__(self, sourceDir, destinationDir):
        self.sourceDir = sourceDir
        self.destinationDir = destinationDir
        self.command = f'/media/kuba/neon/git/robo/rbcx-robotka/mkdocs-doxygen-snippets-plugin/doxygen_snippets/extractDoxygen.sh "Doxygn Snippets" {self.sourceDir} {self.destinationDir}'

    def run(self, print_command: bool = False):
        if print_command:
            print(self.command)
        subprocess.call(shlex.split(self.command))

# class DoxygenRun:
#     def __init__(self, sourceDir, destinationDir):
#         self.destinationDir = destinationDir
#         self.sourceDir = sourceDir
#         self.config = f"""   INPUT             = {self.sourceDir}
#                             EXCLUDE_PATTERNS += *CMake*
#                             FILE_PATTERNS     = *.cpp *.c *.hpp *.h
#                             RECURSIVE         = YES
#                             PROJECT_NAME      = Doxygn Snippets
#                             OUTPUT_DIRECTORY  = {self.destinationDir}
#                             QUIET             = YES
#                             GENERATE_HTML     = NO
#                             GENERATE_LATEX    = NO
#                             GENERATE_XML      = NO
#                             CASE_SENSE_NAMES  = NO
#                             JAVADOC_AUTOBRIEF = YES
#                             AUTOLINK_SUPPORT  = YES
#                             MACRO_EXPANSION   = YES
#                             EXTRACT_ALL       = YES
#                             FULL_PATH_NAMES   = NO"""
#         self.command = f'echo "{self.config}" | doxygen -'
#
#     def run(self, print_command: bool = False):
#         # if print_command:
#             # print(self.command)
#         subprocess.call(shlex.split(self.command))
