from mkdoxy.migration import convert_config_hyphen_version


def test_convert_config_1():
    test_str = """
  - mkdoxy:
      enabled: !ENV [ENABLE_MKDOXY, True]
      projects:
        mkdoxyApi:
          src-dirs: mkdoxy
          full-doc: True
          template-dir: templates-custom
          doxy-cfg-file: demo-projects/animal/Doxyfile
          doxy-cfg:
            FILE_PATTERNS: "*.py"
      save-api: .mkdoxy
      full-doc: True
      debug: False
      ignore-errors: False
    """
    expected_str = """
  - mkdoxy:
      enabled: !ENV [ENABLE_MKDOXY, True]
      projects:
        mkdoxyApi:
          src_dirs: mkdoxy
          full_doc: True
          custom_template_dir: templates-custom
          doxy_cfg_file: demo-projects/animal/Doxyfile
          doxy_cfg:
            FILE_PATTERNS: "*.py"
      custom_api_folder: .mkdoxy
      full_doc: True
      debug: False
      ignore_errors: False
    """
    result = convert_config_hyphen_version(test_str.split("\n"))
    assert result == expected_str.split("\n")


def _test_convert_config(file_old: str, file_new: str):
    with open(file_old, "r") as file:
        lines = file.readlines()

    with open(file_new, "r") as file:
        expected_lines = file.readlines()

    result = convert_config_hyphen_version(lines)
    assert result == expected_lines


def test_convert_config_2():
    _test_convert_config("./tests/data/migration/mkdocs1-old.yaml", "./tests/data/migration/mkdocs1-new.yaml")


def test_convert_config_3():
    _test_convert_config("./tests/data/migration/mkdocs2-old.yaml", "./tests/data/migration/mkdocs2-new.yaml")
