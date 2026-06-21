# Common WInnForum Data & Libraries

Repository location: https://github.com/Wireless-Innovation-Forum/Common-Data.

This repository holds common data related to the Wireless Innovation Forum
[Spectrum Access System](https://github.com/Wireless-Innovation-Forum/Spectrum-Access-System)
and [Automated Frequency Coordination systems](https://github.com/Wireless-Innovation-Forum/6-GHz-AFC)
projects, along with common Python libraries used to work with those data.

Some of the larger geodata files are stored as Git LFS zip archives. Git LFS
downloads those archives from Cloudflare R2 through the endpoint configured in
[.lfsconfig](.lfsconfig):

```
https://winnforum-lfs.winnforum.workers.dev/info/lfs
```

Users do not normally download from Cloudflare directly. Use Git and Git LFS,
then run the extraction scripts below.


## User guide

### Get the data

The full checked-out and extracted data set is about 55 GB. Clone the full data
set only when needed.

Install and enable Git LFS once per machine:

```
git lfs install
```

Clone the repository:

```
git clone https://github.com/Wireless-Innovation-Forum/Common-Data.git
cd Common-Data
```

Extract the NED terrain and NLCD land-cover files:

```
python data/extract_geo.py
```

Extract the county GeoJSON files:

```
python scripts/extract_counties_json.py --extract
```

Do not use GitHub's "Download ZIP" button for this repository. It can leave
large data files as small Git LFS pointer text files instead of real zip files.
If an extraction script reports that a file is not a valid zip, run:

```
git lfs pull
```

Then rerun the extraction command.

If an LFS download fails with an object-not-found or access error, please
contact: https://github.com/glossner

### Download only part of the data

If you only need the source tree or one data directory, skip the automatic LFS
download during clone:

```
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/Wireless-Innovation-Forum/Common-Data.git
cd Common-Data
```

Then pull and extract only the directory you need:

```
# NED terrain tiles
git lfs pull --include="data/ned/*"
python data/extract_geo.py --ned

# NLCD mainland tiles
git lfs pull --include="data/nlcd/*"
python data/extract_geo.py --nlcd

# NLCD island tiles
git lfs pull --include="data/nlcd/nlcd_islands/*"
python data/extract_geo.py --nlcd-islands
```

Only LFS-tracked paths are affected by `git lfs pull --include`. In this
repository, the large LFS-tracked zip files are under [data/ned/](data/ned) and
[data/nlcd/](data/nlcd).

### Population data

The population raster data are currently not provided, although the `usgs_pop`
driver is provided as part of the `winnf` package.

To integrate population data:

1. Download the population data, preferably `pden_2010.zip`, from:
   https://www.sciencebase.gov/catalog/item/57753ebee4b07dd077c70868

2. Unzip the data and put the `pden2010_block/` folder into [data/pop/](data/pop).

### Data integration into SAS

Because the SAS project started before `Common-Data` was migrated into a
standalone data and library repository, the Python modules that read and use the
data are replicated within the SAS repository.

There are three common ways to plug the geo data into SAS:

- Specify the NED and NLCD data locations in
  `src/harness/reference_models/geo/CONFIG.py` of the main
  Spectrum-Access-System repository.
  See https://github.com/Wireless-Innovation-Forum/Spectrum-Access-System/blob/master/src/harness/reference_models/geo/CONFIG.py.

- Create symbolic links in the main SAS repository:
  - `data/geo/ned/` pointing to `Common-Data/data/ned/`
  - `data/geo/nlcd/` pointing to `Common-Data/data/nlcd/`
  - `data/counties/` pointing to `Common-Data/data/counties/`

- Copy the extracted files into `data/geo/ned/`, `data/geo/nlcd/`, and
  `data/counties/` in the SAS repository.

### Data integration into 6GHz-AFC

It is best to use the provided drivers found in the [`winnf`](src/README.md)
module.

```python
import winnf
from winnf.geo import terrain
from winnf.geo import nlcd
from winnf.pop import county

winnf.SetGeoBaseDir('/winnforum/Common-Data/data')

terrain_driver = terrain.TerrainDriver()
nlcd_driver = nlcd.NlcdDriver()
county_driver = county.CountyDriver()

ned_data = terrain_driver.GetTerrainElevation(lats, lons)
```

### NED terrain data

The [data/ned/](data/ned) folder contains the USGS National Elevation Data
(NED) in 1x1 degree tiles with a grid every 1 arcsecond.

Content for each tile:

- `floatnXXwYYY_std.[prj,hdr]`: geo-referencing header files
- `floatnXXwYYY_std.flt`: raw data in ArcFloat format

Some updated tiles use the prefix
`usgs_ned_1_nXXwYYY_gridfloat_std`; these data correspond to newer gathering
techniques, primarily LIDAR.

This reference data corresponds to a snapshot of the latest USGS data available
from July 2017. It is read by the NED terrain driver in
`src/winnf/geo/terrain.py` and used by the WInnForum reference propagation
models in `src/winnf/propag`.

### NLCD land-cover data

The [data/nlcd/](data/nlcd/) folder contains the USGS NLCD National Land Cover
Data, retiled into 1x1 degree tiles with a grid every 1 arcsecond.
See https://www.mrlc.gov/nlcd11_data.php.

Content for each tile:

- `nlcd_nXXwYYY_ref.[prj,hdr]`: geo-referencing header files
- `nlcd_nXXwYYY_ref.int`: raw data

This reference data corresponds to a retiling of the 2011 NLCD data snapshot,
re-released in 2014. The scripts used to create it are documented in
[scripts/](scripts/).

Hawaii and Puerto Rico data were added in 2020. Those island data come from a
2001 source with a reprocess in 2008.

### County data

The [data/counties/](data/counties) folder contains the 2017 FCC county data in
GeoJSON format. The 2017 county data are required for FCC Part 96 calculations.

County data are stored as one GeoJSON file per county. The file name is the
county FIPS/GEOID code. For example, a county with `GEOID="12057013312"` is
stored as `12057013312.json`.


## Developer guide

### Python package

A Python package named `winnf` is provided for reading and working with the geo
data. It is installed from the repository root using `uv` and the root
[pyproject.toml](pyproject.toml). The package does not include the large LFS
data files.

For a local developer install:

```
uv sync
uv run python run_all_tests.py
```

See [src/README.md](src/README.md) for the package details.

### Build distributions

To build the source distribution and wheel:

```
uv run python -m build
```

Do not run `setup.py` directly. It is used by the package build backend; `uv`
will invoke it with the right build commands.

### Optional GDAL support

The `winnf.pop.usgs_pop` module requires `GDAL`/`osgeo`, which depends on the
native GDAL library and headers. Because those native dependencies are
platform-sensitive, GDAL is optional:

```
uv sync --extra pop
```

Without GDAL, population raster tests are skipped and the rest of the package
can still be used.

### Adding new geo files

To add or update LFS-managed geo zip files:

- Copy the new zip files where they belong, normally under `data/ned/` or
  `data/nlcd/`.
- Make sure LFS is activated: `git lfs install`.
- Verify that the file is covered by LFS attributes, for example:
  `git check-attr filter -- data/ned/new_tile.zip`.
- Run `git add path/to/file.zip`.
- Run `git commit`.
- Run `git push`.

The normal `git push` should upload required LFS objects. To explicitly upload
objects referenced by the current commit, use:

```
git lfs push origin HEAD
```

### Data creation scripts

Scripts in [scripts/](scripts/) document the process used to retrieve and
generate the data provided by this repository. Users do not need to run those
scripts unless they want to verify or reproduce the data creation process.

See [scripts/README.md](scripts/README.md) for details.
