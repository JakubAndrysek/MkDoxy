# Changelog
All notable changes to this project will be documented in this file.

- **v1.0.0** - 2023-01-24
    - Initial release
- **v1.0.3** - 2023-03-21
    - Fix: Hash function [support subfolders](https://github.com/JakubAndrysek/MkDoxy/pull/29)
- **v1.0.5** - 2023-04-01
    - Add support for [custom templates](https://github.com/JakubAndrysek/MkDoxy/pull/39)
- **v1.0.6** - 2023-04-01
    - Add support disable plugin [using environment variable](#disabling-the-plugin)
- **v1.1.6** - 2023-07-20
    - Replace `ruamel.yaml` with `pyyaml`. [#73](https://github.com/JakubAndrysek/MkDoxy/pull/73)
    - Add `isort` as dev dependency. [#73](https://github.com/JakubAndrysek/MkDoxy/pull/73)
    - Sort and cleanup imports [#73](https://github.com/JakubAndrysek/MkDoxy/pull/73)
- **v1.1.7** - 2023-11-09
    - Format code using black and add pre-commit config [#77](https://github.com/JakubAndrysek/MkDoxy/pull/77)
    - Fix: add missing package visibility [#80](https://github.com/JakubAndrysek/MkDoxy/pull/80)
...

- **1.2.2** - 2024-04-19
    - Update allowed Jinja extensions
    - Add support for custom Doxygen configuration
- **1.2.3** - 2024-05-6
    - Fix executable not found when the current working directory (cwd) is set to config file path by @wu-vincent in https://github.com/JakubAndrysek/MkDoxy/pull/103
- **1.2.4** - 2024-05-6
    - fix: use absolute links for inherited items by @Nerixyz in https://github.com/JakubAndrysek/MkDoxy/pull/105
- **1.2.5** - 2024-11-22
    - Fixes: brief description in detailed if there is no detailed description; change the Detailed Description header levelby @DmitriyMarin in https://github.com/JakubAndrysek/MkDoxy/pull/114
    - feat: add function in namespace snippet by @barnou-psee in https://github.com/JakubAndrysek/MkDoxy/pull/116
    - add api-path to project configuration by @dustinlagoy in https://github.com/JakubAndrysek/MkDoxy/pull/112
- **1.2.7** - 2025-01-15
    - fix: Improve handling of struct / class initializers by @g-braeunlich in https://github.com/JakubAndrysek/MkDoxy/pull/120
    - fix: Add support for whole spec of doxygen config format by @athackst in https://github.com/JakubAndrysek/MkDoxy/pull/121
- **1.2.8** - 2025-08-29
    - fix: equation rendering by @EmilyBourne in https://github.com/JakubAndrysek/MkDoxy/pull/137
    - fix: bad anchors by @EmilyBourne in https://github.com/JakubAndrysek/MkDoxy/pull/132
