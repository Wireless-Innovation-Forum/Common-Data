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

"""Extract NED and NLCD tiles to be used with reference propagation models.

The zipped tiles are stored in Git LFS under ned/ and nlcd/ folders.
"""

import argparse
import os
import zipfile

# Extract the wanted zipped data files from the given zipfile into the
# given temporary directory.
def UnzipNeededFiles(zip_filename, dest_dir):
  """Unzip all needed geo files from zip.
  """
  if not zipfile.is_zipfile(zip_filename):
    raise Exception(
        '%s is not a valid zip file. If it is a Git LFS pointer, run '
        '`git lfs pull --include="%s"` first.' %
        (zip_filename, os.path.relpath(zip_filename)))
  zf = zipfile.ZipFile(zip_filename, 'r')
  for datfile in zf.infolist():
    if (datfile.filename.endswith('.int') or datfile.filename.endswith('.flt') or
        datfile.filename.endswith('.hdr') or datfile.filename.endswith('.prj')):
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


def main():
  parser = argparse.ArgumentParser(
      description='Extract NED and NLCD zip files downloaded by Git LFS.')
  parser.add_argument(
      '--ned', action='store_true',
      help='Extract NED terrain tiles from data/ned.')
  parser.add_argument(
      '--nlcd', action='store_true',
      help='Extract NLCD land-cover tiles from data/nlcd.')
  parser.add_argument(
      '--nlcd-islands', action='store_true',
      help='Extract NLCD island tiles from data/nlcd/nlcd_islands.')
  args = parser.parse_args()

  extract_all = not (args.ned or args.nlcd or args.nlcd_islands)

  # Find the directory of this script.
  geo_dir = os.path.dirname(os.path.realpath(__file__))

  if extract_all or args.ned:
    ned_dir = os.path.join(geo_dir, 'ned')
    print('Extracting NED data files from zip files in dir=%s' % ned_dir)
    ExtractData(ned_dir)

  if extract_all or args.nlcd:
    nlcd_dir = os.path.join(geo_dir, 'nlcd')
    print('Extracting NLCD data files from zip files in dir=%s' % nlcd_dir)
    ExtractData(nlcd_dir)

  if extract_all or args.nlcd_islands:
    nlcd_dir = os.path.join(geo_dir, 'nlcd', 'nlcd_islands')
    print('Extracting NLCD Islands data files from zip files in dir=%s' %
          nlcd_dir)
    ExtractData(nlcd_dir)


if __name__ == '__main__':
  main()
