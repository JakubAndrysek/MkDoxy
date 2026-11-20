import os
import shutil
import sys

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


def test_check_and_run_persists_hash_only_when_index_xml_exists(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "header.h").write_text("class Foo { ~Foo(); };", encoding="utf-8")
    temp_doxy = tmp_path / "doxy"
    temp_doxy.mkdir()

    monkeypatch.setattr(DoxygenRun, "is_doxygen_valid_path", lambda self, p: True)

    doxygen_run = DoxygenRun(
        doxygenBinPath="doxygen",
        doxygenSource="src",
        tempDoxyFolder="doxy",
        doxyCfgNew={},
    )

    # First run fails to generate xml/index.xml -> raises RuntimeError and hashChanges.yaml must not be persisted
    monkeypatch.setattr(DoxygenRun, "run", lambda self: None)
    with pytest.raises(RuntimeError, match="index.xml"):
        doxygen_run.checkAndRun()
    assert not (temp_doxy / "hashChanges.yaml").exists()

    # Second run creates xml/index.xml -> hashChanges.yaml is persisted and subsequent check returns False
    def fake_success_run(self):
        xml_dir = temp_doxy / "xml"
        xml_dir.mkdir(parents=True, exist_ok=True)
        (xml_dir / "index.xml").write_text("<doxygenindex/>", encoding="utf-8")

    monkeypatch.setattr(DoxygenRun, "run", fake_success_run)
    assert doxygen_run.checkAndRun() is True
    assert (temp_doxy / "hashChanges.yaml").is_file()
    assert doxygen_run.checkAndRun() is False


def test_check_and_run_does_not_persist_hash_when_doxygen_fails_with_existing_index_xml(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    header = src_dir / "header.h"
    header.write_text("class Foo { int a; };", encoding="utf-8")
    temp_doxy = tmp_path / "doxy"
    temp_doxy.mkdir()

    monkeypatch.setattr(DoxygenRun, "is_doxygen_valid_path", lambda self, p: True)

    doxygen_run = DoxygenRun(
        doxygenBinPath="doxygen",
        doxygenSource="src",
        tempDoxyFolder="doxy",
        doxyCfgNew={},
    )

    state = {"returncode": 0, "calls": 0}

    class FakePopen:
        def __init__(self, *args, **kwargs):
            state["calls"] += 1
            self.returncode = state["returncode"]

        def communicate(self, input_bytes):
            xml_dir = temp_doxy / "xml"
            xml_dir.mkdir(parents=True, exist_ok=True)
            (xml_dir / "index.xml").write_text("<doxygenindex/>", encoding="utf-8")
            return (b"", b"simulated failure" if self.returncode else b"")

    monkeypatch.setattr("mkdoxy.doxyrun.Popen", FakePopen)

    # 1. Initial successful run produces index.xml and saves the hash
    assert doxygen_run.checkAndRun() is True
    assert state["calls"] == 1
    assert (temp_doxy / "xml" / "index.xml").is_file()
    assert (temp_doxy / "hashChanges.yaml").is_file()

    # 2. Source files change, but the next Doxygen run fails while stale/partial index.xml exists
    header.write_text("class Foo { int a; int b; };", encoding="utf-8")
    state["returncode"] = 1
    with pytest.raises(RuntimeError, match="exit status 1"):
        doxygen_run.checkAndRun()
    assert state["calls"] == 2
    assert (temp_doxy / "xml" / "index.xml").is_file()
    assert not (temp_doxy / "hashChanges.yaml").exists()

    # 3. Subsequent build must not skip Doxygen; when Doxygen succeeds again, the new hash is saved
    state["returncode"] = 0
    assert doxygen_run.checkAndRun() is True
    assert state["calls"] == 3
    assert (temp_doxy / "hashChanges.yaml").is_file()
    assert doxygen_run.checkAndRun() is False


def test_node_destructor_overline_normalized():
    from xml.etree import ElementTree
    from mkdoxy.constants import Kind
    from mkdoxy.property import Property

    xml_el = ElementTree.fromstring(
        "<memberdef kind='function' id='classFoo_1a1' prot='public'>"
        "<definition>Foo::‾Foo</definition>"
        "<name>‾Foo</name>"
        "<argsstring>()</argsstring>"
        "</memberdef>"
    )
    defn = Property.Definition(xml_el, None, Kind.FUNCTION)
    assert defn.plain() == "Foo::~Foo;"


@pytest.mark.parametrize("exit_code", [0, 7])
def test_run_checks_exit_status_and_reports_output(tmp_path, monkeypatch, exit_code):
    """A subprocess may emit useful output and still report failure."""
    doxygen_run = DoxygenRun(sys.executable, str(tmp_path), str(tmp_path), {})
    # Use a real subprocess with controlled output, without requiring a shell
    # script executable on every platform. Python accepts its program on stdin.
    program = (
        "import sys\n"
        "print('partial generated output')\n"
        "print('generation failed', file=sys.stderr)\n"
        f"sys.exit({exit_code})\n"
    )
    monkeypatch.setattr(doxygen_run, "dox_dict2str", lambda config: program)
    if exit_code:
        with pytest.raises(RuntimeError) as error:
            doxygen_run.run()
        message = str(error.value)
        assert "status 7" in message
        assert "partial generated output" in message
        assert "generation failed" in message
    else:
        doxygen_run.run()


@pytest.mark.skipif(os.name != "posix", reason="Uses an executable script to wrap the real Doxygen")
def test_run_rejects_failure_even_after_xml_generation(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "api.h").write_text("/** Example class. */ class Example {};\n", encoding="utf-8")
    wrapper = tmp_path / "failing-doxygen"
    wrapper.write_text(
        f"#!{sys.executable}\n"
        "import subprocess, sys\n"
        f"subprocess.run([{shutil.which('doxygen')!r}, '-'], check=True)\n"
        "print('error after XML generation', file=sys.stderr)\n"
        "sys.exit(7)\n",
        encoding="utf-8",
    )
    wrapper.chmod(0o755)
    output = tmp_path / "generated"
    output.mkdir()
    doxygen_run = DoxygenRun(str(wrapper), str(source), str(output), {"EXAMPLE_PATH": "", "EXTRACT_ALL": True})
    with pytest.raises(RuntimeError, match="error after XML generation"):
        doxygen_run.run()
    assert (output / "xml" / "index.xml").is_file()
