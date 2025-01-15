import pytest
from mkdoxy.doxyrun import DoxygenCustomConfigNotValid, DoxygenRun


def test_dox_dict2str():
    dox_dict = {
        "DOXYFILE_ENCODING": "UTF-8",
        "GENERATE_XML": True,
        "RECURSIVE": True,
        "EXAMPLE_PATH": "examples",
        "SHOW_NAMESPACES": True,
        "GENERATE_HTML": False,
        "GENERATE_LATEX": False,
    }

    doxygen_run = DoxygenRun(
        doxygenBinPath="doxygen",
        doxygenSource="/path/to/source/files",
        tempDoxyFolder="/path/to/temp/folder",
        doxyCfgNew=dox_dict,
    )

    result = doxygen_run.dox_dict2str(dox_dict)

    expected_result = (
        "DOXYFILE_ENCODING = UTF-8\nGENERATE_XML = YES"
        "\nRECURSIVE = YES\nEXAMPLE_PATH = examples"
        "\nSHOW_NAMESPACES = YES\nGENERATE_HTML = NO"
        "\nGENERATE_LATEX = NO"
    )

    assert result == expected_result


#  Sets the Doxygen configuration using a custom config file
def test_set_doxy_cfg_custom_file():
    dox_dict = {}

    doxygen_run = DoxygenRun(
        doxygenBinPath="doxygen",
        doxygenSource="/path/to/source/files",
        tempDoxyFolder="/path/to/temp/folder",
        doxyConfigFile="./tests/data/Doxyfile",
        doxyCfgNew=dox_dict,
    )

    result = doxygen_run.setDoxyCfg(dox_dict)

    expected_result = {
        "DOXYFILE_ENCODING": "UTF-8",
        "GENERATE_XML": True,
        "RECURSIVE": True,
        "EXAMPLE_PATH": "examples",
        "SHOW_NAMESPACES": True,
        "GENERATE_HTML": False,
        "GENERATE_LATEX": False,
        "INPUT": "/path/to/source/files",
        "OUTPUT_DIRECTORY": "/path/to/temp/folder",
    }

    assert result == expected_result


def test_str2dox_dict():
    dox_str = (
        "DOXYFILE_ENCODING = UTF-8\nGENERATE_XML = YES\n"
        "RECURSIVE = YES\nEXAMPLE_PATH = examples\n"
        "SHOW_NAMESPACES = YES\nGENERATE_HTML = NO\nGENERATE_LATEX = NO"
    )

    doxygen_run = DoxygenRun(
        doxygenBinPath="doxygen",
        doxygenSource="/path/to/source/files",
        tempDoxyFolder="/path/to/temp/folder",
        doxyCfgNew={},
    )

    result = doxygen_run.str2dox_dict(dox_str)

    expected_result = {
        "DOXYFILE_ENCODING": "UTF-8",
        "GENERATE_XML": True,
        "RECURSIVE": True,
        "EXAMPLE_PATH": "examples",
        "SHOW_NAMESPACES": True,
        "GENERATE_HTML": False,
        "GENERATE_LATEX": False,
    }

    assert result == expected_result


def test_str2dox_dict_expanded_config():
    dox_str = (
        "# This is a comment \n"
        "PROJECT_LOGO           =\n"
        'ABBREVIATE_BRIEF       = "The $name class" \\ \n'
        "                         is \n"
        "FILE_PATTERNS          = *.c \n"
        "FILE_PATTERNS          += *.cc\n"
        "PREDEFINED             = BUILD_DATE DOXYGEN=1\n"
    )

    doxygen_run = DoxygenRun(
        doxygenBinPath="doxygen",
        doxygenSource="/path/to/source/files",
        tempDoxyFolder="/path/to/temp/folder",
        doxyCfgNew={},
    )

    result = doxygen_run.str2dox_dict(dox_str)

    expected_result = {
        "PROJECT_LOGO": "",
        "ABBREVIATE_BRIEF": '"The $name class" is',
        "FILE_PATTERNS": "*.c *.cc",
        "PREDEFINED": "BUILD_DATE DOXYGEN=1",
    }

    assert result == expected_result


def test_str2dox_dict_expanded_config_errors():
    doxygen_run = DoxygenRun(
        doxygenBinPath="doxygen",
        doxygenSource="/path/to/source/files",
        tempDoxyFolder="/path/to/temp/folder",
        doxyCfgNew={},
    )

    dox_str = "ONLY_KEY\n"
    error_message = str(
        "Invalid line: 'ONLY_KEY'"
        "In custom Doxygen config file: None\n"
        "Make sure the file is in standard Doxygen format."
        "Look at https://mkdoxy.kubaandrysek.cz/usage/advanced/."
    )

    with pytest.raises(DoxygenCustomConfigNotValid, match=error_message):
        doxygen_run.str2dox_dict(dox_str)

    dox_str = "= ONLY_VALUE\n"
    error_message = str(
        "Invalid line: '= ONLY_VALUE'"
        "In custom Doxygen config file: None\n"
        "Make sure the file is in standard Doxygen format."
        "Look at https://mkdoxy.kubaandrysek.cz/usage/advanced/."
    )

    with pytest.raises(DoxygenCustomConfigNotValid, match=error_message):
        doxygen_run.str2dox_dict(dox_str)

    dox_str = "KEY WITH SPACES = VALUE\n"
    error_message = str(
        "Invalid line: 'KEY WITH SPACES = VALUE'"
        "In custom Doxygen config file: None\n"
        "Make sure the file is in standard Doxygen format."
        "Look at https://mkdoxy.kubaandrysek.cz/usage/advanced/."
    )

    with pytest.raises(DoxygenCustomConfigNotValid, match=error_message):
        doxygen_run.str2dox_dict(dox_str)

    dox_str = "BAD_OPERATOR := VALUE\n"
    error_message = str(
        "Invalid line: 'BAD_OPERATOR := VALUE'"
        "In custom Doxygen config file: None\n"
        "Make sure the file is in standard Doxygen format."
        "Look at https://mkdoxy.kubaandrysek.cz/usage/advanced/."
    )

    with pytest.raises(DoxygenCustomConfigNotValid, match=error_message):
        doxygen_run.str2dox_dict(dox_str)

    dox_str = "BAD_MULTILINE = BAD\n" "                VALUE\n"
    error_message = str(
        "Invalid line: '                VALUE'"
        "In custom Doxygen config file: None\n"
        "Make sure the file is in standard Doxygen format."
        "Look at https://mkdoxy.kubaandrysek.cz/usage/advanced/."
    )

    with pytest.raises(DoxygenCustomConfigNotValid, match=error_message):
        doxygen_run.str2dox_dict(dox_str)
