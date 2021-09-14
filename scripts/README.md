# Data retrieval and processing scripts

This folder holds all scripts that were used to retrieve and preprocess
geo data found in this repository: `data/ned`, `data/nlcd` and `data/counties`.
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
      

## Process for recreating counties GeoJSON
we have two options to get the county data:
	1.extracting the converted zipped files, which are in "https://github.com/Wireless-Innovation-Forum/Spectrum-Access-System/tree/master/data/counties/ manually or by running:
		`$ python extract_counties_json.py --extract`
	2.Convert and split the raw county data file from https://github.com/Wireless-Innovation-Forum/Common-Data/tree/master/data/counties/2017_county_boundaries_raw_data.zip, this file was downloaded from the source https://fcc.maps.arcgis.com/home/item.html?id=19cd330160eb4297b58bc8dccd49a61a which is referenced on https://www.fcc.gov/35-ghz-band-overview 
		for this option we need to convert this source file to individual geojson county files by providing the
	 command line option --convert
		`$ python extract_counties_json.py --convert`
		
the resulted json files should be placed in https://github.com/Wireless-Innovation-Forum/Spectrum-Access-System/tree/master/data/counties

### Usage and Sample Output
   <pre>
   <code>
   <b> $ python extract_counties_json.py -h </b>
   usage: extract_counties_json.py [-h] (--extract | --convertt)

   optional arguments:
       -h, --help  show this help message and exit
	   --extract only extract the zipped data.
       --convert convert and split the raw county data file to idividual json data.
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
  

