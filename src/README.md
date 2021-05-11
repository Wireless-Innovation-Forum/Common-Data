# `winnf`: The Winnforum common libraries

The `winnf` python package holds common Winnforum modules.

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

### `prop` subpackage

It provides radio propagation modules such as:
 * `itm`: the ITM (Longley-Rice) propagation model
 * `ehata`: the NTIA E-Hata propagation model

### `pop` subpackage

It provides population-related modules:
 * `census`: to read the census tracts database
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

### Preliminary

Only Python3 is officially supported.

It is also recommended to use the `anaconda` python installer. You can use 
either the `full` distribution (see https://www.anaconda.com/distribution/)
or the `mini` distribution (https://docs.conda.io/en/latest/miniconda.html).

For the miniconda distribution (recommended), you will have to install manually 
the  required individual packages, using the `conda install` instruction:
see section below for full example.

Note: if you are using another python distribution, follow the specific
instruction for that distribution. Usually you can use `pip` for installing
new modules: 
>> pip3 install --user attrs
Using pip within conda is possible although not recommended. 

The following will assume that you use `miniconda`.

### Required packages

The following third party packages are required:

 + `shapely`: geometry on the plane
 + `pykml`: for KML parsing
 + `numpy`: matlab-like numerical maths
 + `six`: compatibility model for Python3 migration
 + `gdal`: gdal/osr geo packages

### Example using miniconda
A complete installation of all required module can be done using conda as following:

+ Install python 3.7 in its own environment
>> conda create -n py37 python=3.7 conda

+ Activate the newly created environment
>> conda activate py37

+ Install packages (other dependency installed transitively)
>> conda install -c conda-forge shapely
>> conda install -c conda-forge numpy
>> conda install -c conda-forge gdal
>> pip3 install pykml
>> pip3 install six
>> etc...

+ work & play ...

+ After finishing work, go back to system level python
>> conda deactivate


### Compilation

The provided propagation models require compilation.

Follow the instructions in the README.md file for your achitecture at:
  [winnf/propag/itm/README.md](winnf/propag/itm/README.md)


### Module visibility 

Make sure that the `winnf` package is in a directory specified in your `PYTHONPATH`.

Another option is to locally install the `winnf` package, by using the `pip` utility:
 - go into the top `Common-Data/src/` directory
 - `pip3 install .`

==> This will install the package locally in your computer into the appropriate installation directory.

### Running all unit tests

All unit test can be run as following from the top directory:

>> python3 -m unittest discover -p '*_test.py'

or simply using the shell script:

>> [./run_all_tests.sh](winnf/run_all_tests.sh)


