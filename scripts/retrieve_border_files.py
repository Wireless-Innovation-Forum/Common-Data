#    Copyright 2015 SAS Project Authors. All Rights Reserved.
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

# This script retrieves relevant static FCC files. These include definitions
# of grandfathered protection sites, definitions of national borders, and
# other relevant data. The script writes the files into the data/fcc directory.

import os

from six.moves import urllib


# Retrieve the url passed to the current directory. Writes the file using
# the filename of the passed URL.
def RetrieveURL(url):
  parsed = urllib.parse.urlparse(url)
  path = parsed.path.split('/')
  filename = path[-1]
  print('Retrieving file %s from %s ...' % (filename, parsed.netloc))
  raw = urllib.request.urlopen(url)
  if not raw.getcode() == 200:
    raise Exception('Could not find %s file' % filename)

  with open(filename, 'wb') as out:
    while True:
      c = raw.read(64*1024)
      if not c:
        break
      out.write(c)
  raw.close()
  print('Retrieved file %s from %s' % (filename, parsed.netloc))


# Find the directory of this script.
cur_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(cur_dir)
dest_dir = os.path.join(os.path.join(root_dir, 'data'), 'zones', 'parts')

print('Retrieving border files to dir=%s' % dest_dir)
if not os.path.exists(dest_dir):
  os.makedirs(dest_dir)
os.chdir(dest_dir)


# Retrieve needed files

# The following US/Canada forder file cannot be found anymore in this site.
# RetrieveURL('https://transition.fcc.gov/oet/info/maps/uscabdry/uscabdry.zip')

# The Mexican border file
RetrieveURL('http://www.ibwc.gov/GIS_Maps/downloads/us_mex_boundary.zip')

# The NOAA maritime boundaries
RetrieveURL('http://maritimeboundaries.noaa.gov/downloads/USMaritimeLimitsAndBoundariesKML.kmz')
