from mkdoxy.doxyrun import DoxygenRun


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
