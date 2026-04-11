# Changelog

## 0.1.12

- Add Excalidraw integration for interactive graph visualization in Jupyter notebooks
  - `to_excalidraw(directed_only=False)` — converts graph to Excalidraw JSON format
  - `show_excalidraw(width, height, view_mode, directed_only)` — renders an interactive
    SVG canvas inline in a notebook cell (no external dependencies or CDN required)
  - `save_excalidraw(filepath, directed_only)` — exports graph as a `.excalidraw` file
    that can be opened at excalidraw.com
- Interactive features: pan (drag background), zoom (scroll wheel), drag nodes
- Nodes are laid out in a circular arrangement; all five edge types (`-->`, `o->`,
  `<->`, `---`, `o-o`) are mapped to the corresponding arrowheads
- Edge colors and labels (strength, pvalue) are preserved in the output

## 0.1.11

- In `modify_existing_edge`, if edge doesn't exist skip instead of raising an error.
  This supports using a subset of edges (e.g. ancestors) with full graph SEM results.

## 0.1.10

- Add `directed_only` boolean to `load_graph`, `save_graph`, `show_graph` to only
  include directed edges (`-->`, `o->`).

## 0.1.9

- Change the handling of arguments for `save_graph`.

## 0.1.8

- Add `exclude` option to `add_edges` method to exclude certain edge types.
- Add support for `---` edge in `load_graph` method.

## 0.1.7

- Add `add_edges` method to add multiple edges at once.

## 0.1.6

- Fixed bug with adding the `<->` edge type.

## 0.1.5

- Change `modify_existing_edge` to use `self.dot` object.

## 0.1.4

- Add `show_graph` method to display graph in Jupyter notebook.

## 0.1.3

- Have `__init__` create the graph dict, new format for graph structure.

## 0.1.2

- Default resolution of 300.

## 0.1.1

- Added `GENERAL|gvinit` to set graph attributes.

## 0.1.0

- Initial version.
