# Owned image fixtures

`src/image_example.h` refers to seven real images with Doxygen `@image html`.
`mkdocs.yml` sets `IMAGE_PATH: images`. Doxygen copies the inputs to its XML
output; MkDoxy then copies and registers them for the final MkDocs site.

- `images/pipeline.svg` is authored SVG source.
- `generate_assets.py` creates the PNG, JPG, JPEG, animated GIF, BMP and WebP
  examples directly from drawing commands. They are illustrations, not measured
  project metrics. JPG and JPEG are two extensions of the same encoding.

Normal tests use the versioned images and require no Pillow. To regenerate the
raster inputs, use Pillow 12.1.1 and run `python generate_assets.py`. Review the
resulting binary differences rather than automatically refreshing fixtures.
Regeneration may differ with a different Pillow version.

Each of the eight integration configurations checks all seven images in XML,
Markdown, HTML and the final site, including byte-for-byte asset comparisons.
Recursive copier tests use synthetic bytes to check path and extension handling;
those tests are separate from these real renderable inputs.
