# Common Winnforum Data & Libs

Repository location: https://github.com/Wireless-Innovation-Forum/Common-Data. 

This Github repository holds all common data related to the Wireless Innovation Forum [Spectrum Access System](https://github.com/Wireless-Innovation-Forum/Spectrum-Access-System) and [Automated Frequency Coordination systems](https://github.com/Wireless-Innovation-Forum/6-GHz-AFC) projects, along with some common libraries used to use those data.

Note that some of the data are stored with Git LFS (Large File Storage) extension and requires special installation procedure described below.


## WARNING

The full data is about about 50 GB in size. 
Because of quota limitation, please only clone when necessary. 
If cloning fails, it can be that the transfer quota has been reached for the month. In that case, please contact:
  https://github.com/LeePucker

The recommended way to obtain the data is to use GIT. 
Any other method such as direct download from GitHub website is not ensured
to give proper results, and you can end up only with small tracker text files. 
In that case, see section below "Retrieving the raw files from LFS" to recover
the full binary files using GIT command line.


## Library: `winnf` package

A python package is provided for reading and working with the geo data.
This package provides a number of sub packages of interest for Winnforum projects.

See dedicated [src/README.md](src/README.md) for a complete description.


## Data retrieval

### Cloning the repository
Clone this repository using GIT.

```
    git clone https://github.com/Wireless-Innovation-Forum/Common-Data.git
```

In case you do not have GIT LFS already installed and enabled, these files are not real
zip files yet, but simple text trackers to the LFS (Large File Storage) storage.


### Retrieving the raw files from LFS

If not already done, install `git-lfs` for your architecture by referring to the GitHub LFS page:
https://git-lfs.github.com/

To actually get the real data stored in LFS, you need to perform:

```
    # Install git lfs (if not already done)
    git lfs install
    
```

Then pull the data (ie fetch and checkout):

```
    git lfs pull
```

### Extracting the ned and nlcd zip files

To actually unzip the ned and nlcd tiles, you can use the provided script 
`data/extract_geo.py`:

```
    python extract_geo.py
```

This will extract all the ned and nlcd zip files in place.

### Extracting the county zip file

To only unzip the county json files from the zip file, you can use the 
provided script `script/extract_counties_json.py`:

```
    python extract_counties_json.py --extract
```

This will extract all counties json files from the zip file in place.


### Population data

The population raster data is currently not provided, although the `usgs_pop` driver
is provided as part of the `winnf` package.

It is easy to integrate:

1. Download the population data (preferable pden_2010.zip) from:
    https://www.sciencebase.gov/catalog/item/57753ebee4b07dd077c70868

2. Unzip the data and put the `pden2010_block/` folder into the [`data/pop/`](data/pop) folder.



## Data integration into SAS

Because the SAS project was started before the `Common-Data` repository was migrated
into a set of standalone modules+data, the python module that reads & use the data
are replicated within the SAS repository. 

This also means a specific process for plugging the geo data for use by these SAS modules:

+ One way is to specify the location of your NED and NLCD data location in the file
`src/harness/reference_models/geo/CONFIG.py` of the main Spectrum-Access-Systems repository.
(See: https://github.com/Wireless-Innovation-Forum/Spectrum-Access-System/blob/master/src/harness/reference_models/geo/CONFIG.py).

+ Another recommended way is to create soft links (with unix command `ln -s`) in the 
main SAS repository:
   - `data/geo/ned/`  pointing to `Common-Data/data/ned/`
   - `data/geo/nlcd/`  pointing to `Common-Data/data/nlcd/`
   - `data/counties/` pointing to `Common-Data/data/counties/`

+ The last option is to copy (or move) the extracted files into a folder `data/geo/ned/`,
`data/geo/nlcd` and `data/counties` of the SAS repository (which are the default 
target of the CONFIG.py file).


## Data integration into 6GHz-AFC

It is best to use the provided drivers found in the [`winnf`](src/README.md) module.

```python
# Import the winnf modules.
import winnf
from winnf.geo import terrain
from winnf.geo import nlcd
from winnf.pop import county

# Initialize the module data location.
winnf.SetGeoBaseDir('/winnforum/Common-Data/data')

# Create drivers towards the geo data
terrain_driver = terrain.TerrainDriver()
nlcd_driver = nlcd.NlcdDriver()
county_driver = county.CountyDriver()

# Read the data.
ned_data = terrain_driver.GetTerrainElevation(lats, lons)
etc...
```


## Data Description

### NED Terrain data

The [data/ned/](data/ned) folder contains the USGS National Elevation Data (NED) in 1x1 degrees tiles 
with grid every 1 arcsecond.

Content for each tile:

  - floatnXXwYYY_std.[prj,hdr] : geo referencing header files
  - floatnXXwYYY_std.flt : raw data in ArcFloat format.

An updated version of some of the tiles are provided with the prefix usgs_ned_1_nXXwYYY_gridfloat_std: these data correspond to newer data gathering techniques (primarily LIDAR).

NOTE: This reference data corresponds to a snapshot of the latest USGS data available from July 2017.

The data is read by the NED terrain driver found in `src/winnf/geo/terrain.py`, 
and in particular is used by the Winnforum reference propagation models in `src/winnf/propagation`.

Header files are provided for enabling the data to be displayed on any GIS tool.

### NLCD Land Cover data

The [data/nlcd/](data/nlcd/) folder contains the data for the USGS NLCD (National Land Cover Data), 
retiled in 1x1 degrees tile with grid every 1 arcsecond. See:  https://www.mrlc.gov/nlcd11_data.php


Content for each tile:

  - nlcd_nXXwYYY_ref.[prj,hdr] : geo referencing header files
  - nlcd_nXXwYYY_ref.int : raw data

This reference data corresponds to a retiling operation of the original NLCD data snapshot 
of 2011 (re-released in 2014), using the set of following (provided) scripts:

 - `scripts/retrieve_orig_nlcd.py`: retrieve the original 2011 NLCD data
 - `scripts/retile_nlcd.py`: retile the data into 1x1 degrees tiles with grid point at
 multiple of 1 arcsecond.

The retiled data can be read by the NLCD driver found in `src/wflib/geo/nlcd.py`.

They can be displayed in any GIS tool, thanks to header files provided for georeferencing.

Note: because SAS is defined to use NLCD only at multiple of 1 arcseconds (for PPA/WISP zones
mainly), the present retiling does not loose information compared to the original geodata
in the original Albers projection.

#### Case of Islands data

An update was performed in 2020 by introducing missing data for Hawaii and Puerto Rico. 
The extraction generation script have been updated accordingly.

Note: The data source is from 2001 with a reprocess in 2008.


### County Data

The [data/counties/] folder contains the data for the 2017 FCC county data 
in geojson format. The 2017 county is required as per the FCC rule part.96 requirements.

All the county data are stored in one county per file in geojson format with
the file name being the fips code (aka. GEOID in the coutny term) of the 
corresponding county. For example, for a county with "STATEFP"="12",
"COUNTYFP"="057","TRACTCE"="013312","GEOID"="12057013312", the file name is `12057013312.json`.

They can be displayed in any web site with geojson display capability.

County data is used for calculations in, for example, PPA reference model.

## Adding new geo files

To add or update existing files to the `Common-Data` LFS repository:
 
  - copy the new zip files where they belong
  - make sure LFS is activated: `git lfs install`
  - `git add *.zip`
  - `git commit`
  - `git push`

## Scripts used for data creation

A number of scripts are provided in the [`scripts/`](scripts/) folder. 

These scripts are provided only for documenting exactly the process that was used to retrieve
and generate the data that are provided by the `Common-Data` repository.

You **DO NOT need** to run those scripts unless you want to verify the process.

See the [scripts/README.md](scripts/README.md) file.

## Counties
The [data/counties/] folder contains the data for the 2017 defined using the United States Census Bureau’s 2017 counties 
in geojson format. The 2017 county data is required as per the FCC rule part.96 requirements.

All the county data are stored in one county per file in geojson format with
the file name being the fips code (aka. GEOID in the county data term) of the 
corresponding county. For example, for a county with "STATEFP"="12",
"COUNTYFP"="057","TRACTCE"="013312","GEOID"="12057013312", the file name is `12057013312.json`.

They can be displayed in any web site with geojson display capability.

county data is used for calculations in, for example, PPA reference model.