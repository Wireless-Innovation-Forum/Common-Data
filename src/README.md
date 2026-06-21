# `winnf`: The WInnForum common libraries

The `winnf` Python package holds common WInnForum modules.

## Content
This package provides a number of sub packages:

### `geo` subpackage

This subpackage provides a number of modules to:
 * `terrain`: driver to read the NED terrain
 * `nlcd`: driver to read the NLCD land cover data
 
It also provides a bunch of modules of use in Winnforum projects:
 * `zones`: to read various US border geometries
 * `vincenty`: for geodesic computations
 * `utils`: a compilation of useful geo routines

### `propag` subpackage

It provides radio propagation modules such as:
 * `itm`: the ITM (Longley-Rice) propagation model
 * `ehata`: the NTIA E-Hata propagation model

### `pop` subpackage

It provides population-related modules:
 * `county`: to read the county database
 * `usgs_pop`: access to population density from USGS population rasters
 
See specific documentation in [`winnf/pop/README.md`](winnf/pop/README.md).


### Module Initialization

Before calling the geo routines in some client code, one needs to initialize
the data location used by the package, for example:

```python
import winnf
winnf.SetGeoBaseDir('/winnforum/Common-Data/data')
```
(assuming the Common-Data folder has been put in such location).


## Installation instructions

The modern install is managed from the repository root with `uv`. It creates a
local `.venv`, installs the package in editable mode, and builds the compiled
ITM and E-Hata propagation extensions.

Python 3.9 or newer is supported.

```
cd /path/to/Common-Data
uv sync
```

The core package dependencies are:

 * `numpy`: numerical arrays and math
 * `pykml`: KML parsing
 * `shapely`: planar geometry
 * `six`: compatibility helpers retained by the existing code

The large terrain, land-cover, county, and population data files are not bundled
into the Python package. They remain repository data files and should be
downloaded with Git LFS as described in the top-level README.

### Optional population raster support

The `winnf.pop.usgs_pop` module requires `GDAL`/`osgeo`, which depends on the
native GDAL library and headers. Because those native dependencies are
platform-sensitive, GDAL is optional rather than part of the core install:

```
uv sync --extra pop
```

If `GDAL` is difficult to install on a target machine, the rest of the package
can still be used without this extra. The county population helper does not
require `GDAL`.

### Building a wheel

To build the source distribution and wheel:

```
uv run python -m build
```

The wheel contains the Python code and compiled propagation extensions. It does
not include the large Common-Data LFS data directories.

### Running all unit tests

Run the unit tests from the repository root:

```
uv run python run_all_tests.py
```

Some population raster tests are skipped unless `GDAL`/`osgeo` is installed.

### Legacy/manual compilation notes

The package build compiles the propagation extensions automatically. The legacy
manual build notes are still available for troubleshooting at:
  [winnf/propag/itm/README.md](winnf/propag/itm/README.md)
