# Contributing to MkDoxy

Thank you for helping maintain MkDoxy. Small, focused fixes, regression tests,
documentation improvements and reviews are welcome. Discuss larger changes in
an issue before implementing them so we can agree on scope and compatibility.
Please follow the [Code of Conduct](CODE_OF_CONDUCT.md). Report vulnerabilities
privately using [SECURITY.md](SECURITY.md).

## Development setup

Work from the repository root. Install Git, [uv](https://docs.astral.sh/uv/getting-started/installation/)
(version 0.13.8, matching CI) and the Doxygen executable. On Debian/Ubuntu,
Doxygen is available through `sudo apt-get install doxygen`; other platforms
should use their package manager or the [Doxygen downloads](https://www.doxygen.nl/download.html).

```sh
uv sync --locked --extra dev
uv run --locked --extra dev python --version
doxygen --version
```

uv creates `.venv` and installs this checkout in editable mode. `.python-version`
selects Python 3.14 for local development; uv can download it if needed. The
versioned `uv.lock` fixes Python dependency resolution, not the Doxygen executable
or OS packages. Tests that construct `DoxygenRun` also
validate its executable path, so install Doxygen even for the current unit suite.

pip remains supported; uv is not a runtime requirement:

```sh
python -m venv .venv
# POSIX shells; Windows PowerShell: .venv\Scripts\Activate.ps1
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The build backend is `uv_build`, a separate build-time package that pip installs
automatically when needed. pip users do not need the uv executable. Metadata and
file selection live in `pyproject.toml`; `setup.py` and `MANIFEST.in` are no longer
used. Jinja templates under `mkdoxy/` are packaged with the module. Source
distributions also include the tests and compatibility requirement files.

`requirements.txt` and `devdeps.txt` remain compatibility installers for `.` and
`.[dev]` respectively; run them from the repository root. Edit dependency metadata
in `pyproject.toml`, not those files. pip installations use the declared version
ranges, not uv.lock. After an intentional dependency change, run `uv lock`, review
the lockfile diff and verify the supported interpreters. CI uses `--locked` to
reject stale metadata rather than silently regenerate the lockfile.

## Current compatibility and tools

`pyproject.toml` declares Python >=3.10, and CI covers Python 3.10-3.15 on
Ubuntu 24.04. This records the existing configuration, not a guarantee that all
those interpreters still receive upstream security updates. Use a maintained
interpreter for normal development and preserve the declared syntax/API minimum
until a dedicated compatibility change is reviewed.

Python 3.10 and 3.11 compatibility is retained while modernizing testing.
The reference interpreter for lint and documentation deployment is Python 3.14;
this does not raise the package's syntax/API minimum. To exercise another
interpreter, pass it explicitly, for example:

```sh
uv run --locked --extra dev --python 3.10 pytest tests/
```

The pytest CI matrix uses the same locked environment. Documentation and demo
jobs also exercise the pip development extra for compatibility. The existing
Black/Ruff hooks remain unchanged; broader typing and regression coverage are
separate follow-up work.

## Verification

Run relevant tests from the repository root:

```sh
uv run --locked --extra dev pytest tests/
uv run --locked --extra dev pre-commit run --all-files
uv run --locked --extra dev mkdocs build --clean
```

To run pre-commit automatically before each local commit, install its local Git
hook explicitly:

```sh
uv run --locked --extra dev pre-commit install
```

Hook installation is local to your checkout. CI still runs the checks when a
workflow is allowed to start. Review incoming hook configuration, build backends
and dependency changes before running them: pre-commit executes hooks; it is not
a sandbox for untrusted contributions.

- `tests/` is the maintained pytest suite. `tests-old/` is historical material
  outside that suite.
- The packaging regression builds a wheel from a source distribution in a
  temporary directory, reusing the installed backend without a separate build environment.
  It verifies metadata, templates and the MkDocs entry point. It does not publish.
- Pre-commit currently runs whitespace/end-of-file checks, Black and Ruff. It
  downloads its own hook environments on first use. Hooks can modify files;
  inspect and commit the intended fixes, then rerun until clean.
- The documentation build exercises Doxygen and the plugin using local example
  sources. Review its diagnostics and generated output, not only the exit code.
- Existing CI also builds the separate
  [MkDoxy-demo](https://github.com/JakubAndrysek/MkDoxy-demo) repository at a pinned
  commit. The demo build checks that dependency installation has not replaced the
  candidate MkDoxy checkout. Update the pinned ref in
  `.github/workflows/mkdoxy-test-demos.yaml` only after reviewing the demo changes
  and verifying them with the candidate plugin.

For packaging changes, also build and inspect the distributions:

```sh
uv run --locked --extra dev python -m build
uv run --locked --extra dev python -m twine check dist/*
```

Check that the wheel and sdist retain Jinja templates, runtime metadata and the
`mkdocs.plugins` entry point. Do not run `make release`, `make release-test`,
`twine upload` or `mkdocs gh-deploy` as validation commands: they publish artifacts
or documentation. Publishing is a separate owner-coordinated action.

## Integration tests

Small, repository-owned C++ and MkDocs projects live under
`tests/integration/fixtures/`. The pytest builder copies each fixture to a fresh
temporary directory and invokes the current interpreter's `mkdocs build --clean
--strict` with real Doxygen. Generated XML, Markdown, HTML, caches and a
`build.log` stay in that directory; the fixture and developer caches are not
modified. Output is streamed to the log even on failure or timeout. On the Linux
CI runners, a timeout terminates the entire build process group, including
Doxygen. Windows uses `taskkill /T`; that cleanup path is not covered by the
Linux process-lifetime regression test. The subprocess receives a minimal
environment without inherited credentials, and imports MkDoxy from the candidate checkout. This environment
is for reproducibility, not a sandbox for untrusted code.

Run only integration tests or the remaining tests with:

```sh
uv run --locked --extra dev pytest tests/ -m integration -v
uv run --locked --extra dev pytest tests/ -m "not integration"
```

The existing `pytest tests/` CI command includes both. Doxygen must be on PATH;
a missing executable, a build timeout or a failed strict build fails the test
rather than silently skipping it. A nonzero Doxygen exit status fails the build
and reports its stdout and stderr even if XML was already generated. Use
pytest's `--basetemp` option to choose a location for retained artifacts (pytest clears that directory before the run).
The OS-provided Doxygen version is not locked; include its version when reporting
failures. External demo builds remain a broader smoke test, not the source of
these focused fixtures.

The first fixture covers parameter names, descriptions, unannotated parameters,
and `[in]`, `[out]`, `[in,out]` annotations. Tests verify the input XML and the
resulting Markdown and HTML, including the actual API hyperlink and its target.
A `doxy.api.class.method` snippet also verifies all three directions and an
unannotated parameter in the rendered HTML.
Directions render before parameter names as `[in]`, `[out]` and `[in/out]`; an
unannotated parameter keeps its existing output. These regression tests cover
issue #78 and the implementation contributed in PR #147. All are normal,
required assertions, without expected-failure marks.

## CI checks and permissions

CI uses distinct check names: `pre-commit`, `pytest (Python X.Y)`,
`docs (Python X.Y)` and `demo (Python X.Y)`. The matrix checks cover the Python
versions listed in the workflows. Keep these names stable once they are required
by branch protection. `pre-commit` retains its existing name so the current
required check continues to run during the transition.

Versioned workflows default to `contents: read`. Test and lint checkouts do not
persist Git credentials. Only the documentation deployment job has
`contents: write` and persisted credentials, needed by `mkdocs gh-deploy` to push
`gh-pages`; that workflow runs only on pushes to `main`. Actions are pinned to
full commit SHAs. Review the source and compatibility when updating a pin.

Workflow changes do not update GitHub's repository settings. After the new check
names have appeared in a successful pull request run, the owner can add all
matrix checks to the required checks for `main`. Do not require a deployment
check that runs only after a merge, and do not remove the existing lint gate
before its replacement has run successfully.

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
