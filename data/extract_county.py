#    Copyright 2017 SAS Project Authors. All Rights Reserved.
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

"""Extract USGS County data.

The zipped tiles are stored in Git LFS under county/ folders.
"""

import os
import zipfile

# Extract the wanted zipped data files from the given zipfile into the
# given temporary directory.
def UnzipNeededFiles(zip_filename, dest_dir):
  """Unzip all needed geo files from zip.
  """
  zf = zipfile.ZipFile(zip_filename, 'r')
  for datfile in zf.infolist():
    if (datfile.filename.endswith('.json')):
      try:
        zf.extract(datfile, dest_dir)
      except:
        raise Exception('Cannot extract ' + datfile.filename +
                        ' from ' + zip_filename)

def ExtractData(directory):
  for f in os.listdir(directory):
    if f.endswith('.zip'):
      # Check if already extracted
      UnzipNeededFiles(os.path.join(directory, f), directory)

# Find the directory of this script.
geo_dir = os.path.dirname(os.path.realpath(__file__))

county_dir = os.path.join(geo_dir, 'counties')
print 'Extracting County data files from zip files in dir=%s' % county_dir
ExtractData(county_dir)

