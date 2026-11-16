# Contributing to MkDoxy

Thank you for helping maintain MkDoxy. Small, focused fixes, regression tests,
documentation improvements and reviews are welcome. Discuss larger changes in
an issue before implementing them so we can agree on scope and compatibility.
Please follow the [Code of Conduct](CODE_OF_CONDUCT.md). Report vulnerabilities
privately using [SECURITY.md](SECURITY.md).

## Development setup

Work from the repository root in a virtual environment. Install a Python version
compatible with `setup.py`, Git and the Doxygen executable. On Debian/Ubuntu,
Doxygen is available through `sudo apt-get install doxygen`; other platforms
should use their package manager or the [Doxygen downloads](https://www.doxygen.nl/download.html).

```sh
python -m venv .venv
# POSIX shells; Windows PowerShell: .venv\Scripts\Activate.ps1
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
doxygen --version
```

The editable install must refer to this checkout. Doxygen is a separate system
dependency; pip does not install it. Tests that construct `DoxygenRun` also
validate its executable path, so install Doxygen even for the current unit suite.

## Current compatibility and tools

`setup.py` declares Python >=3.10, and CI covers Python 3.10-3.15 on
Ubuntu 24.04. This records the existing configuration, not a guarantee that all
those interpreters still receive upstream security updates. Use a maintained
interpreter for normal development and preserve the declared syntax/API minimum
until a dedicated compatibility change is reviewed.

Python 3.10 and 3.11 compatibility is retained while modernizing testing.
The reference interpreter for lint and documentation deployment is Python 3.14;
this does not raise the package's syntax/API minimum. uv and expanded typing are
planned follow-up work; they are not implemented by this document. The commands below use today's pip,
pytest and pre-commit setup. Update this guide when those tools change.

## Verification

Run relevant tests from the repository root:

```sh
python -m pytest tests/
python -m pre_commit run --all-files
mkdocs build --clean
```

- `tests/` is the maintained pytest suite. `tests-old/` is historical material
  outside that suite.
- Pre-commit currently runs whitespace/end-of-file checks, Black and Ruff. It
  downloads its own hook environments on first use. Hooks can modify files;
  inspect and commit the intended fixes, then rerun until clean.
- The documentation build exercises Doxygen and the plugin using local example
  sources. Review its diagnostics and generated output, not only the exit code.
- Existing CI also builds the separate
  [MkDoxy-demo](https://github.com/JakubAndrysek/MkDoxy-demo) repository. Its inputs
  currently follow its default branch, so record the demo revision and confirm
  the candidate MkDoxy installation when investigating differences.

For packaging changes, also build and inspect the distributions:

```sh
python -m build
python -m twine check dist/*
```

Check that the wheel and sdist retain Jinja templates, runtime metadata and the
`mkdocs.plugins` entry point. Do not run `make release`, `make release-test`,
`twine upload` or `mkdocs gh-deploy` as validation commands: they publish artifacts
or documentation. Publishing is a separate owner-coordinated action.

## Reproducing and fixing a bug

1. Capture a minimal input and the expected result. Include relevant MkDoxy,
   Python, MkDocs and Doxygen versions, configuration and diagnostics.
2. Add a regression test that fails on the old implementation and passes with
   the fix. Prefer small, owned fixtures; retain license and attribution when
   reusing external material.
3. Check the affected output: Markdown content/order, HTML links and anchors,
   copied assets or the Doxygen/cache state sequence, as appropriate.
4. Run related tests and describe limitations. If a problem needs Doxygen or a
   complete MkDocs build to reproduce, include those steps rather than relying
   only on mocks. Temporary inputs and output must not reuse a developer cache.

Do not encode an unrelated known bug as the expected behavior of a new feature.
Keep baseline failures distinguishable from regressions. Changes to generated
output need a reviewed explanation; a successful build alone is insufficient.

## Pull requests and AI-assisted work

Use a branch or fork and keep each PR focused. Its description should explain:

- The problem and related issue, with a concrete before/after example if useful.
- The resulting behavior and any compatibility or dependency changes.
- What was tested, the results, and any tests that were not run.

Coding agents are welcome. The submitting contributor remains responsible for
understanding the diff, checking generated suggestions, respecting licenses and
providing reproducible evidence. Follow [AGENTS.md](AGENTS.md); it is a short
guide to the repository, not a requirement to use a particular AI product.

Use an issue/PR description for a small fix. For a larger design change, agree
on a concise proposal covering requirements, scope, compatibility and acceptance
criteria. Keep durable decisions in documentation and behavior in tests; leave
raw conversations, prompts and temporary investigation logs out of the repo.

When continuing an older contribution, preserve original authorship and credit
the original PR. If a replacement PR is needed, explain the relationship and
link it; avoid duplicating work without coordination.

Collaborator access, release preparation and publishing permissions are separate
from contribution acceptance. They are coordinated with the repository owner.
Submissions retain the project's existing [MIT license](LICENSE).
