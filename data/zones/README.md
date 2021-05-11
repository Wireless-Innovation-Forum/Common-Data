This directory contains various zones of interest for spectrum work.

## US-Canada border

The US-Canada border is represented by a KML file having gone through a workflow.


* `uscabdry.kml`
    
    This is a KML file produced by the script in `scripts/uscabdry.py`. 
    It contains the US-CA border as processed from the KMZ source file with
    data reduction, normalization, and some noise removal.

* `uscabdry_resampled.kml`

    This is a KML file produced by the script in `scripts/resample_uscabdry.py`.
    It is the same file as `uscabdry.kml` with new vertices injected along the border so that 
    the distance between 2 consecutive vertices do not exceed 200m.
    Using this resampling allows for deterministically finding the closest point on the border, 
    by selecting the closest vertex.


## US general border

The US general border is described by the `usborder.kml` KML file,  which is 
produced by the script in `scripts/usborder.py`. 

It contains polygons representing the border represented by the territorial sea 
boundary of US jurisdiction as modified by international sea borders reflected
in the NOAA files, and modified by border definitions for US-CA and US-MEX, as
defined by the `us_mex_boundary` and `uscabdry_resampled.kml` files.


## US urban area

The `Urban_Areas_3601.kmz` holds the official urban area as defined by the census bureau.
