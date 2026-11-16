# Testing and CI

Use this guide when adding fixtures, reproducing output regressions or changing
CI. The [contributing guide](https://github.com/JakubAndrysek/MkDoxy/blob/main/CONTRIBUTING.md)
contains development setup, compatibility policy and the pull request process.
For user-facing configuration and required diagram tools, see
[Images and diagrams](../usage/images-and-diagrams.md).

## Run the maintained suite

Install Doxygen and the locked development environment from the contributing
guide, then run from the repository root:

```sh
uv run --locked --extra dev pytest tests/ -q
uv run --locked --extra dev pre-commit run --all-files
```

`tests/` is maintained; `tests-old/` contains historical experiments. pytest's
`integration` marker selects the real Doxygen/MkDocs builds. The remaining
tests include focused parser/copier checks, packaging and runner failure tests.
The locked Python environment does not pin OS tools such as Doxygen.

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
environment without inherited credentials, and imports MkDoxy from the candidate
checkout. This environment is for reproducibility, not a sandbox for untrusted code.

Run only integration tests or the remaining tests with:

```sh
uv run --locked --extra dev pytest tests/ -m integration -v
uv run --locked --extra dev pytest tests/ -m "not integration"
```

The existing `pytest tests/` CI command includes both. Doxygen must be on PATH;
a missing executable, a build timeout or a failed strict build fails the test
rather than silently skipping it. A nonzero Doxygen exit status fails the build
and reports its stdout and stderr even if XML was already generated. Use
pytest's `--basetemp` option to choose a location for retained artifacts
(pytest clears that directory before the run).
The OS-provided Doxygen version is not locked; include its version when reporting
failures. External demo builds remain a broader smoke test, not the source of
these focused fixtures.

### Parameter directions

The parameter fixture covers names, descriptions, unannotated parameters,
and `[in]`, `[out]`, `[in,out]` annotations. Tests verify the input XML and the
resulting Markdown and HTML, including the actual API hyperlink and its target.
A `doxy.api.class.method` snippet also verifies all three directions and an
unannotated parameter in the rendered HTML.
Directions render before parameter names as `[in]`, `[out]` and `[in/out]`; an
unannotated parameter keeps its existing output. These are normal assertions, without expected-failure marks.

### Image assets

The image fixture uses Doxygen `@image` comments and seven owned, renderable
SVG, PNG, JPG, JPEG, animated GIF, BMP and WebP inputs (JPG/JPEG share an encoding).
Tests resolve the actual HTML image URL to a site file and compare its bytes
with the source asset. They cover default and nested `api-path`, the default
cache location and custom `save-api`, and both directory and flat HTML URLs.
The typed `BuildOptions` passed to `build_project` selects these variants. An
optional `prepare` callback modifies only the temporary fixture copy before
loading configuration, for example to reproduce existing asset collisions;
fixtures keep a single project named `api`. Focused copier tests separately
cover nested XML assets and supported extensions because Doxygen itself may
flatten image paths in its XML output. Regression cases also cover overlapping
XML/API paths, copy failures, source and destination symlink escapes, and
identical versus conflicting existing docs assets. See the fixture README and optional
`generate_assets.py` for image provenance. The separate
`demo-projects/diagrams/` examples show native Doxygen-generated graphs; these
are not automatically rendered by MkDoxy and require Graphviz to regenerate.

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
