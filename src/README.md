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

Python 3.15 is the current target, with backward compatibility through Python
3.11. The dependency resolver selects compatible NumPy releases on older Python
versions. A C++ compiler is required to build the ITM and E-Hata extensions.

```
cd /path/to/Common-Data
uv python install 3.15.0
uv sync --locked
```

The core package dependencies are:

 * `numpy`: numerical arrays and math
 * `pykml`: KML parsing
 * `shapely`: planar geometry
 * `sciencebasepy`: USGS ScienceBase downloads

The large terrain, land-cover, county, and population data files are not bundled
into the Python package. They remain repository data files and should be
downloaded with Git LFS as described in the top-level README.

### Population raster downloads and optional GDAL support

The `winnf.pop.usgs_pop` module requires `GDAL`/`osgeo`, which depends on the
native GDAL library and headers. Because those native dependencies are
platform-sensitive, GDAL is optional rather than part of the core install:

```
uv sync --locked --extra pop
```

If `GDAL` is difficult to install on a target machine, the rest of the package
can still be used without this extra. The county population helper does not
require `GDAL`.

Population raster files can be downloaded from USGS ScienceBase with the
top-level helper script. The script queries ScienceBase by DOI, then lists or
downloads the attached `pdenYYYY_block.zip` files:

```
uv sync --locked
uv run --locked python scripts/download_population.py
uv run --locked python scripts/download_population.py 2010
```

### Building a wheel

To build the source distribution and wheel:

```
uv build
```

Do not run `setup.py` directly. It is used by the package build backend; `uv`
will invoke it with the right build commands.

The wheel contains the Python code and compiled propagation extensions. It does
not include the large Common-Data LFS data directories.

### Running all unit tests

Run the unit tests from the repository root:

```
uv sync --locked --extra test
uv run --locked --extra test python run_all_tests.py
```

Some population raster tests are skipped unless `GDAL`/`osgeo` is installed.
The Python GDAL version must match the installed native GDAL library. For
example, after installing the native headers, use
`uv pip install "GDAL==$(gdal-config --version)"`. The unit tests include the
original NTIA propagation examples to verify that numeric results are preserved.

### Legacy/manual compilation notes

The package build compiles the propagation extensions automatically. The legacy
manual build notes are still available for troubleshooting at:
  [winnf/propag/itm/README.md](winnf/propag/itm/README.md)
