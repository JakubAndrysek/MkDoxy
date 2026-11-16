# Native Doxygen diagrams

These owned examples distinguish generated diagrams from the existing-image
copying feature in MkDoxy. Run `doxygen Doxyfile` here with Graphviz `dot` on
PATH; open `output/html/index.html`. Doxygen generates its own native HTML/XML.
These diagrams are not currently rendered automatically by MkDoxy's XML parser.

- `gallery.h`: inline `@dot`, `@dotfile`, inline `@msc`, and `@mscfile`.
- `model.h`: inheritance, collaboration, call and caller graphs from C++ code.
  Its inclusion by `gallery.h` also generates include dependency graphs.
- `states.dot`: explicit Graphviz graph definition.
- `exchange.msc`: explicit message sequence chart definition.
- `Doxyfile`: enables Graphviz, SVG output and automatic graph types.

This is an optional native-Doxygen demonstration, not part of the mandatory
MkDoxy image-copy regression tests. The latter require no Graphviz or Pillow.
PlantUML and Dia require additional tools; no generated examples for them are
claimed here. Available diagram commands also depend on the Doxygen version.

## Combined visual gallery

Run from the repository root:

```sh
uv run --locked --extra dev python demo-projects/diagrams/build_gallery.py
```

The command creates a fresh temporary directory and prints its site path. It
builds the image fixture with MkDoxy and native Doxygen diagrams in both SVG and
PNG. The Material gallery separates imported image formats from native diagrams
and provides their actual input sources. It does not implement automatic graph
rendering in MkDoxy, publish a site or add mandatory CI dependencies.

The image-fixture README describes the authored SVG and raster generator. Only
regenerating raster inputs requires Pillow; consuming them does not.

The user-facing [Images and diagrams guide](../../docs/usage/images-and-diagrams.md)
lists prerequisites and installation commands. To explicitly refresh its static
illustrations, run the gallery command with `--export-docs-assets`; review the
resulting SVG changes under `docs/media/diagrams/`.
