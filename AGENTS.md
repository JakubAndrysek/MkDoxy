# Working on MkDoxy

Read [CONTRIBUTING.md](CONTRIBUTING.md) for setup, verification commands,
compatibility and the pull request process. Those instructions apply to both
people and coding agents. Use [SECURITY.md](SECURITY.md) for vulnerability reports
and follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Repository map

- `mkdoxy/plugin.py`: MkDocs lifecycle, project configuration and generated files.
- `mkdoxy/doxyrun.py`: Doxygen configuration, subprocess execution and source cache.
- `mkdoxy/doxygen.py`, `node.py`, `finder.py`, `cache.py`: XML-backed symbol model
  and lookup. Paths in this list are relative to `mkdoxy/` after the first entry.
- `mkdoxy/xml_parser.py`, `markdown.py`, `property.py`: XML content and Markdown
  rendering.
- `mkdoxy/generatorAuto.py`, `generatorBase.py`, `generatorSnippets.py` and
  `mkdoxy/templates/`: full documentation, indexes and Markdown directives.
- `tests/`: collected pytest tests and fixtures. `tests-old/` contains historical
  experiments; it is not the maintained test suite.
- `demo-projects/`, `docs/`, `mkdocs.yml`: inputs and documentation for this repo.
- `setup.py`, `requirements.txt`, `devdeps.txt`: current packaging and dependencies.
- `.github/workflows/`: tests, documentation builds, lint and Pages deployment.

## Change and review expectations

- Preserve the currently declared Python compatibility. Read `setup.py` and CI;
  do not introduce newer syntax or raise the minimum as an incidental refactor.
- Follow existing local naming/style. Keep broad renames and formatting changes
  separate from behavioral changes.
- Add a focused regression test for a bug. Verify the generated output as well
  as the build exit status; missing content and broken links may not fail a build.
- Treat Markdown paths, anchors, templates, directive syntax, ordering and cache
  behavior as compatibility concerns. Do not refresh expected output without
  reviewing the difference.
- Use the verification commands in CONTRIBUTING. Report what actually ran,
  versions where relevant, and any checks that could not run. A proposed test
  or a bot review is not a successful execution.
- Document the final behavior and important decisions. Keep chat transcripts,
  prompts, scratch scripts and session logs out of project documentation.
- A dependency, workflow, packaging or release change needs explicit review of
  its effects. Do not include publishing or access changes in an unrelated fix.
- Respect the task's authorization. Preparing a PR does not itself authorize
  merging, releasing, changing credentials or modifying collaborator access.

These are working instructions, not an access-control mechanism. Do not assume
branch protections, release approval or other safeguards exist just because a
document describes the intended process.
