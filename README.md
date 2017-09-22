# SAS-Data

This repository holds all data related to the [Wireless Innovvation Forum / Spectrum Access System](https://github.com/Wireless-Innovation-Forum/Spectrum-Access-System) GitHub repository,
which are stored in Git LFS (Large File storage).

## Data integration in SAS environment

The SAS repository integrates these data as a submodule in `data/geo/`.

### Integrating the submodule
If you are already in the SAS code repository and see this file, it means that the submodule
has already been integrated and you do not need to perform this step.

If you do not wish to manage the geodata as part of the SAS repository as a submodule:

 - you can ignore this step and go directly to next steps about LFS data fetching
 and zip extraction.
 - make sure the `src/harness/reference_models/geo/CONFIG.py` settings point
 to your data locations.

Otherwise if you wish to manage the data as a submodule of the SAS repository, 
simply perform the following steps after the SAS repository cloning:

```
    # Get the actual data into a 'geo' submodule
    git submodule update --init
```

You should now see the `data/geo` folder with a bunch of zip files in the subfolders. 
These files are not real zip files yet, but simple text trackers to the LFS (Large File Storage) storage.

Alternatively to update the `data/geo` folder after the initial update, you can do:

```
    cd data/geo
    git pull
```

### Retrieving the raw files from LFS

To actually get the real data stored in LFS, you need to perform:

```
    # Install git lfs (if not already done)
    git lfs install
    
```

Then go to the geo directory, and pull the data (ie fetch and checkout):

```
    cd data/geo
    git lfs pull
```

### Extracting the zip files

To actually unzip the tiles, you can use the script provided in `src/data/`:

```
    python extract_geo.py
```

### Managing things

To disable Git LFS and avoid any future pull on the data:

```
    git lfs uninstall
```

To remove the geodata submodule entirely, if you decide to move it elsewhere, you can use:

```
    git submodule deinit --all
```

In that case, make also sure to specify the location of your final data location in the file
`src/harness/reference_models/geo/CONFIG.py`.


## NED Terrain data

The `ned/` folder contains the USGS National Elevation Data (NED) in 1x1 degrees tiles with grid every 1 arcsecond.

Content for each tile:

  - floatnXXwYYY_std.[prj,hdr] : geo referencing header files
  - floatnXXwYYY_std.flt : raw data in ArcFloat format.

An updated version of some of the tiles are provided with the prefix usgs_ned_1_nXXwYYY_gridfloat_std: 
this data corresponds to newer data gathering techniques (primarily LIDAR).

This reference data corresponds to a snapshot of the latest USGS data available from July 2017.

The data is read by the NED terrain driver found in harness/src/reference_models/geo/terrain.py, 
and in particular is used by the reference propagation models in harness/src/reference_models/propagation.

Header files are provided for enabling the data to be displayed on any GIS tool.

## NLCD Land Cover data

The `nlcd/` folder contains the data for the USGS NLCD (National Land Cover Data), retiled in 1x1 degrees tile with grid every 1 arcsecond.

Content for each tile:

  - nlcd_nXXwYYY_ref.[prj,hdr] : geo referencing header files
  - nlcd_nXXwYYY_ref.int : raw data

This reference data corresponds to a retiling operation of the original NLCD data snapshot of 2014, 
using the set of following (provided) scripts:

 - `src/data/retrieve_orig_nlcd.py`: retrieve the original 2014 NLCD data
 - `src/data/retile_nlcd.py`: retile the data into 1x1 degrees tiles with grid point at multiple of 1 arcsecond.

The retiled data can be read by the NLCD driver found in harness/src/reference_models/geo/nlcd.py, and displayed in any GIS tool.

Header files are provided for enabling the data to be displayed on any GIS tool.

Note: because SAS is defined to use NLCD only at multiple of 1 arcseconds (for PPA/WISP zones mainly), the present retiling 
does not loose information compared to the original geodata in the original Albers projection.



