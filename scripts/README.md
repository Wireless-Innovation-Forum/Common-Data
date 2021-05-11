# Data retrieval and processing scripts

This folder holds all scripts that were used to retrieve and preprocess
geo data found in this repository: `data/ned`, `data/nlcd` and `data/census`.
It also holds some common border data in `data/zones`.

These scripts are provided only for documenting the process in generating
those data. 

You DO NOT need to run the scripts unless you want to verify the process.

Note: the sripts are supporting both Python2 and Python3, but the
original data were generated using Python2.

## Process for creating NED terrain database

Warning for SAS: 
> this procedure shall not be run for replicating the official NED database to be
> used by SAS, as it would recreate a different snapshot than the official one which
> was created mainly in July 2017. Use data provided in the repository `ned/` folder
> to use the official one.
>
> Any future official update will be done by Winnforum and published in this repository.


The NED terrain tiles are provided directly from USGS FTP site in 1x1 degrees tiles.

Tiles are simply retrieved using the two scripts:

  - `retrieve_orig_ned.py`: retrieves all 1 arcsec resolution tiles from USGS FTP site.
    Final tiles are put in a folder `data/ned_out/`
  - `retrieve_alaska_ned_extra.py`: complete the previous set with missing Alaska tiles
    using Alaska 2-arcsec database and a resampling to 1 arcsec. 
    Final tiles are put in a folder `data/ned_out2/`
  - add manually the data in `Common-Data` repository (under `ned/` folder)
  
Please note that these 2 scripts keep track of the original downloaded data in 
directories `data/orig_ned` and `data/orig_ned2`. 
Subsequent run of the script will only download and process new updated tiles.


## Process for recreating NLCD tiles from scratch

The NLCD tiles have been created with the following process:

 - `retrieve_orig_nlcd.py`: retrieve the original NLCD 16GB CONUS geodata
 - unzip the retrieved zipped files.
 - `retile_nlcd.py` : process the original NLCD into 1x1 degrees tiles with grid
   at multiple of 1 arcsecond. 

Note that the retile script requires a complete NED terrain database available,
as it build NLCD tiles only where corresponding NED tile are available.
So this process shall be done after a snapshot of the NED terrain tile is built.
      

## Process for recreating census tract GeoJSON

There are three steps to recreate the census tract GeoJSON database as follows:

  1. Download all original census tract data from the USGS web site. 
       `$ python extract_census_tracts_json.py --retrieve`
    `Spectrum-Access-System/data/census` will be created and all original census tract 
    shapefile will be downloaded into this directory. Note that the current GitHub 
    repository provide that directory with the original files from 2010 Census, so this
    step is unnecessary.

  2. Convert the shape files to GeoJSON.
       `$ python extract_census_tracts_json.py --convert`
    The shapefile from directory `Spectrum-Access-System/data/census` will be converted
    to GeoJSON file within the same directory.

  3. Split the GeoJSON file into individual census tract files based on GEOID.
       `$ python extract_census_tracts_json.py --split`
    The converted census tract files will be split in individual GeoJSON tract file
    and dumped into the `Spectrum-Access-System/data/census_tracts` directory.

### Usage and Sample Output
   <pre>
   <code>
   <b> $ python extract_census_tracts_json.py -h </b>
   usage: extract_census_tracts_json.py [-h] (--retrieve | --convert | --split)

   optional arguments:
       -h, --help  show this help message and exit
       --retrieve  Download original census tract data from the USGS web site.
       --convert   Convert the shape file to GeoJSON.
       --split     Split census tract files into individual based on FISP code.
   </pre>
   </code>
  

## Border related geo data

US border related geo data are provided for:
 - US/Canada border
 - General US border
 - US Urban areas (as defined by census bureau)

### Retrieving data

The required composite data is retrieved using the scripts:

 - `retrieve_border_files.py`: Retrieves the US-Mexican and US-Canada original file from
 FCC online database, and NOAA maritime boundaries.
 Note: The US-canada file is no more available from the FCC site, and the retrieval of that
 file has been disabled for now - use the provided file instead.
 

### Pre-Processing US-Canada border

The US-Canada border is processed by the following scripts in order:

 - `uscabdry.py`: Takes the `uscabdry.kmz` file holding a set of independent geometries, 
 and convert it into a clean `uscabdry.kml` file holding a single LineString geometry with
 all duplication and artifacts removed.
 
 - `resample_uscabdry.py`: Takes the `uscabdry.kml` file obtained by previous step and 
 produces a `uscabdry_resampled.kml` file where  new vertices are added in order to have 
 no more than 200m between 2 consecutive vertices. 
 The generated KML file is suitable for deterministic characterization of closest border 
 points by simple selection of closest vertex, as required by border protection reference 
 model.
 

### Forming the general US border file

The general `usborder.kml` file is created by the script `usborder.py` which blends
together the following KML/KMZ files:
 
  - `data/zones/uscabdry.kml`: the refined US-Canada border.
  - `data/zones/parts/us_mex_boundary_kmz`: the US-Mexico border.
  - `data/zones/parts/USMaritimeLimitsAndBoundariesKML.kmz`: The maritime boundaries.
  

