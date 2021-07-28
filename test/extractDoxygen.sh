#!/usr/bin/env bash

usage="Usage: $0 <projectName> <sourceDir> <destinationDir> [project defines]"

if [ "$#" -ne 3 ] && [ "$#" -ne 4 ]; then
    echo "Invalid arguments"
    echo $usage
    exit 1
fi

if ! [ -e "$3" ]; then
    mkdir -p $3
fi

cfg=$(cat <<END
    INPUT             = $2
#    EXCLUDE_PATTERNS += *_deps* *build* *test*
    EXCLUDE_PATTERNS += *CMake*
    FILE_PATTERNS     = *.cpp *.c *.hpp *.h
    RECURSIVE         = YES
    PROJECT_NAME      = $1
    OUTPUT_DIRECTORY  = $3
    QUIET             = YES
    GENERATE_HTML     = NO
    GENERATE_LATEX    = NO
    GENERATE_XML      = NO
    CASE_SENSE_NAMES  = NO
    JAVADOC_AUTOBRIEF = YES
    AUTOLINK_SUPPORT  = YES
    MACRO_EXPANSION   = YES
    EXTRACT_ALL       = YES
    FULL_PATH_NAMES   = NO
    PREDEFINED        += $4
END
)

(echo "$cfg";  echo "GENERATE_XML = YES") | doxygen -
(echo "$cfg";  echo "GENERATE_HTML = YES") | doxygen -