#    Copyright 2021 Winnforum Authors. All Rights Reserved.
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
import os
import unittest

import numpy as np
import shapely.geometry as sgeo
from shapely import ops

from winnf.geo import zones
import winnf

winnf.SetGeoBaseDir(
    os.path.join(os.path.dirname(os.path.realpath(__file__)),
                 '..', '..', '..', 'data'))


class TestZones(unittest.TestCase):
  # Simplistic tests which only check the proper reading of the files.
  def test_read_urban_areas(self):
    z = zones.GetUrbanAreas()
    exp_area = 275000
    approx_area = z.area * 110**2 * np.cos(44*np.pi/180)
    self.assertTrue(z.is_valid)
    self.assertTrue(approx_area > exp_area * 0.9 and
                    approx_area < exp_area * 1.1)

  def test_read_usborder(self):
    z = zones.GetUsBorder()
    self.assertTrue(z.is_valid)
    us_area = 9.8e6
    approx_area = z.area * 110**2 * np.cos(44*np.pi/180)
    self.assertTrue(approx_area > us_area * 0.9 and
                    approx_area < us_area * 1.1)

  def test_read_uscanadaborder(self):
    borders = zones.GetUsCanadaBorder()
    self.assertTrue(borders.is_valid)
    # Official length of main and alaska are resp 3987 miles and 1538 miles
    exp_borders_length = sum(np.array([3987, 1538]) * 1.60934)
    approx_len = 0
    for j, border in enumerate(borders):
      points = list(zip(*border.xy))
      for k in range(len(points)-1):
        if points[k][0] > -67.8 and points[k][1] < 44.77:
          continue  # the border file includes a maritime part not accounted in border length
        dlat = points[k+1][1] - points[k][1]
        dlon = points[k+1][0] - points[k][0]
        d = np.sqrt((dlat * 111)**2 + (dlon * 111 * np.cos(points[k][1]*np.pi/180.))**2)
        approx_len += d
    self.assertTrue(abs(approx_len - exp_borders_length) < 40)


if __name__ == '__main__':
  unittest.main()
