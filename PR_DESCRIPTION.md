# feat: Git clone support and automatic nav injection for remote sources

## Summary

Adds the ability to use a remote Git repository as the documentation source for a MkDoxy project. The plugin clones the repository at build time, runs Doxygen against it, and automatically injects the generated API pages into a specified section of the MkDocs navigation.

## Changes

### New features

- **Git clone support** (`git-url`, `git-branch`, `git-recursive` config options): When `git-url` is set for a project, MkDoxy clones the repository at build time using a shallow clone (`depth=1`) and uses it as the source for Doxygen. Submodule recursion can be enabled via `git-recursive`.
- **Automatic nav injection** (`parent-nav-section` config option): After generating the API docs, the plugin reads the generated `links.md` and injects the resulting nav entries into a named section of the MkDocs `nav` config. The section is located recursively, so it works at any nesting level.
- **`rewrite_nav()` function**: Parses `links.md`, builds nav entries, and calls `get_navigation()` to rebuild the MkDocs navigation with the new entries inserted.
- **`cleanup_temp_dir()` helper**: Removes the temporary directory created for the git clone after all projects have been processed.

### Implementation details

- Replaced `TemporaryDirectory` context manager with `tempfile.mkdtemp()` so the cloned repository persists for the full duration of the build.
- `src-dirs` path is built by joining the clone root with the configured subdirectory; defaults to the clone root if `src-dirs` is not a string.
- Git clone errors are handled separately for `GitExc.GitCommandError` (with `stderr` extraction) and generic exceptions, both logged and re-raised as `ConfigurationError`. Respects the `ignore-errors` flag.

