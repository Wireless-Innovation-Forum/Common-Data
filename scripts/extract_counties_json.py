#    Copyright 2016-2018 SAS Project Authors. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
"""extract_counties_json utility to convert counties data to individual json files
  or to extract already converted data.

This extract_counties_json.py will help to perform following operations:
1.Convert and split the raw counties data, which are in a zip, to individual geojson counties files by providing the
 command line option --Convert
2.extract already converted counties files from a zip file by providing the command line option --extract

'Spectrum-Access-System/data/counties' directory will be used as a source to convert/extract raw/converted
 counties data and as a destination directory for the individual counties files by prefix GEOID as file name.
"""
import argparse
import glob
import io
import json
import os
import re
import shapefile
import sys
import zipfile
import shapely.geometry as sgeo
from collections import OrderedDict



def ExtractZipFiles(counties_directory, zip_filename=None):
  """Extract the counties file downloaded from www.fcc.gov"""
  # Filter the zip filename based on specified file name if any ends with .zip
  counties_file_list = [os.path.join(counties_directory, f)
                             for f in os.listdir(counties_directory)
                             if all((True if not zip_filename else
                                     f.startswith(zip_filename),
                                     f.endswith('.zip')))]
  if  len(counties_file_list) == 0:
    raise Exception('no zip file was found in %s' %counties_directory)           
  for file_name in counties_file_list:
    # Check if already extracted.
    zf = zipfile.ZipFile(file_name, 'r')
    for datfile in zf.infolist():
      if any((datfile.filename.endswith('.dbf'),
              datfile.filename.endswith('.prj'),
              datfile.filename.endswith('.shp'),
              datfile.filename.endswith('.shp.xml'),
              datfile.filename.endswith('.shx'),
              datfile.filename.endswith('.json'))):
        try:
          zf.extract(datfile, counties_directory)
        except:
          raise Exception('Cannot extract ' + datfile.filename +
                          ' from ' + zip_filename)


def json_pp_dumps(obj, **kw):
  """Pretty json.dumps replacement."""
  return json.dumps(json.loads(json.dumps(obj),
                               parse_float=lambda f: round(float(f), 7),
                               object_pairs_hook=OrderedDict),
                   **kw)


def ConvertShapefilesToGeoJson(counties_directory):
  """Convert Shapefile to GeoJson."""
  print("Convert the Shapefiles to GeoJson format")

  # Extract all files before convert to shapely.
  ExtractZipFiles(counties_directory)

  # Proceed further to convert to geojson.
  os.chdir(counties_directory)
  shp_files = glob.glob('*.shp')

  try:
    for shp_file in shp_files:
      # Read the shapefile and fields
      reader = shapefile.Reader(shp_file)
      fields = reader.fields[1:]
      field_names = [field[0] for field in fields]

      # Sanity check that GEOID, ALAND and AWATER present
      # Needs a loop to check if tag is within each string
      has_geoid = any('GEOID' in field for field in field_names)
      has_aland = any('ALAND' in field for field in field_names)
      has_awater = any('AWATER' in field for field in field_names)
      if not has_geoid or not has_aland or not has_awater:
        raise Exception('Could not find GEOID,ALAND,AWATER in fields %r' % fields)

      records = []
      for shp_record in reader.shapeRecords():
        properties = dict(zip(field_names, shp_record.record))
        geometry = shp_record.shape.__geo_interface__
        records.append(OrderedDict([('type','Feature'),
                                    ('properties',properties),
                                    ('geometry',geometry)]))

      # Write the GeoJSON file.
      base_name = os.path.splitext(shp_file)[0]
      json_file =  base_name + '.json'
      with open(json_file, 'w') as fd:
        fd.write(json_pp_dumps(
            OrderedDict([('type','FeatureCollection'),
                         ('name', base_name),
                         ('features',records)])))
        fd.write('\n')
      print(shp_file + " was converted to " + json_file + ".")

  except Exception as err:
    raise Exception("There is an issue in ConvertShapefilesToGeoJson: %s"
                    % err.message)


def SplitCountiesGeoJsonFile(counties_directory):
  """Split counties GeoJson file with mulitiple single file based on FISP Code."""
  try:
    print("\n" + "Splitting files..." + "\n")
    os.chdir(counties_directory)
    json_files = glob.glob('*.json')
    # split all counties based on FISP code and dump into separate directory
    with open('warnings.log', 'w') as logger:
     for json_file in json_files:
      with open(json_file, 'r') as fd:
        features = json.loads(fd.read(),
                              object_pairs_hook=OrderedDict)['features']

      for feature in features:
        fisp_code = None
        # Check for properties object that includes the field GEOIDXX and get that value
        # of GEOIDXX and assign it as file_name to split GeoJSON records.
        for field_name in feature['properties']:
           if field_name.startswith('GEOID'):
             fisp_code = feature['properties'][field_name]
             break
        if not fisp_code:
          raise Exception('Unable to find GEOID property in county')

        # Check for validity of the geometry
        shape = sgeo.shape(feature['geometry'])
        if not shape.is_valid:
          logger.write('Shapely geometry invalid for file: %s FISP: %s '
                       % (json_file, fisp_code))

        out_path = os.path.join(counties_directory, fisp_code + '.json')
        with open(out_path, 'w') as fd:
          fd.write(json_pp_dumps(OrderedDict([('type','FeatureCollection'),
                                              ('features',[feature])]),
                                 separators=(',', ':')))
          fd.write('\n')

        print("counties of fispCode: %s record split to the file:%s "
              "successfully" % (fisp_code, out_path))

  except Exception as err:
    raise Exception("There is issue in spliting counties file : %s"
                    % err.message)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument(
      '--convert', help='Convert the counties shape file to GeoJSON individual files based on FISP code',
      dest='convert', action='store_true')
  group.add_argument(
      '--extract', help='extract county files from zip to folder',
      dest='extract', action='store_true')
  try:
    args = parser.parse_args()
    print(args)
  except:
    parser.print_help()
    sys.exit(0)

  # Find the counties directory and
  # create the dest directory if not exists.
  root_directory = os.path.dirname(os.path.dirname(
      os.path.realpath(__file__)))
  counties_directory = os.path.join(os.path.join(root_directory, 'data'),
                                  'counties')  
  if not os.path.exists(counties_directory):
    raise Exception("counties directory doesn't exist : %s"
                    % counties_directory)

  if args.convert:
    # Convert the shapely file to individual GeoJSON files.
    print('All counties will be converted into individual GeoJSON files based on FISP code and placed '
          'in directory:%s' % counties_directory)
    ConvertShapefilesToGeoJson(counties_directory)
    SplitCountiesGeoJsonFile(counties_directory)

  if args.extract:
    print('All files in archive will be extracted in directory:%s'
          % counties_directory)
    ExtractZipFiles(counties_directory)
