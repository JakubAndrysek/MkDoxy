from pathlib import Path


def replace_tags_in_mkdoxy_config(file_name: Path) -> None:
    with open(file_name, "r") as file:
        lines = file.readlines()

    new_config = convert_config_hyphen_version(lines)

    with open(file_name, "w") as file:
        file.writelines(new_config)


def convert_config_hyphen_version(lines: list[str]) -> list[str]:
    translation_dict = {
        "src-dirs": "src_dirs",
        "full-doc": "full_doc",
        "doxy-cfg-file": "doxy_cfg_file",
        "save-api": "custom_api_folder",
        "template-dir": "custom_template_dir",
        "ignore-errors": "ignore_errors",
        "doxy-cfg:": "doxy_cfg:",
    }

    inside_mkdoxy = False
    updated_lines = []

    for line in lines:
        if "mkdoxy:" in line:
            inside_mkdoxy = True

        if inside_mkdoxy:
            for old_key, new_key in translation_dict.items():
                if old_key in line:
                    line = line.replace(old_key, new_key)

            if line.strip() == "" or (line.strip().startswith("- ") and "mkdoxy:" not in line):
                inside_mkdoxy = False
        updated_lines.append(line)

    return updated_lines


def update_new_config(
    path_to_mkdocs: Path, backup_old_config: bool = True, backup_file_name: str = "mkdocs.old.yaml"
) -> None:
    """
    Copy current config to mkdocs.old.yaml and update mkdocs.yaml with new config
    @details
    @param path_to_mkdocs: Path to mkdocs folder
    @param backup_old_config: Backup old config to mkdocs.old.yaml - default True
    @param backup_file_name: Name of backup file - default "mkdocs.old.yaml"
    """
    print(path_to_mkdocs)
    if not path_to_mkdocs.is_file():
        raise FileNotFoundError(f"File {path_to_mkdocs} not found")

    if backup_old_config:
        mkdocs_old = path_to_mkdocs.with_name(backup_file_name)

        # copy mkdocs_new config to mkdocs.old.yaml
        mkdocs_old.write_text(path_to_mkdocs.read_text())

    # update mkdocs_new config
    replace_tags_in_mkdoxy_config(path_to_mkdocs)