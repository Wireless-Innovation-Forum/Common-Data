This directory contains raw data files used to derive some border related files.
These are typically retrieved from official sources using the `retrieve_border_files.py` 
script.


* `USMaritimeLimitsAndBoundariesKML.kmz`

    Raw file defining US maritime boundaries. This file is referred to here:
    https://www.fcc.gov/encyclopedia/white-space-database-administration-q-page
    and here: http://www.nauticalcharts.noaa.gov/csdl/mbound.htm
    and can be retrieved here:
    http://maritimeboundaries.noaa.gov/downloads/USMaritimeLimitsAndBoundariesKML.kmz

    This file is only use by the `usborder.py` script, which produces a composite US
    border file.

* `us_mex_boundary.zip` and `us_mex_boundary.kmz`

    This is the raw zip file containing the FCC definition of the US-Mexico
    border. It is linked from this page:
    https://www.fcc.gov/encyclopedia/white-space-database-administration-q-page
    and can be retrieved here:
    http://www.ibwc.gov/GIS_Maps/downloads/us_mex_boundary.zip

    The KMZ file is an exact representation of the boundary line
    contained in the `us_mex_boundary.zip` Shapefile.

* `uscabdry.zip` and `uscabdry.kmz`

    This is the raw zip file containing the FCC definition of the US-Canada
    border. It is linked from this page:
    https://www.fcc.gov/encyclopedia/white-space-database-administration-q-page
    and can be retrieved here:
    https://transition.fcc.gov/oet/info/maps/uscabdry/uscabdry.zip

    The KMZ file is an exact representation of the boundary lines contained
    in the uscabdry.zip file. There are 17 line segments composing this
    boundary, each taken from a separate .MAP file in the `uscabdry.zip` file.
