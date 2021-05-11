#    Copyright 2020 Winnforum Authors. All Rights Reserved.
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
"""Tests for usgs_pop."""
import os
import unittest

import numpy as np

from winnf.pop import usgs_pop

TESTDATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'testdata')


class UsgsPopTest(unittest.TestCase):

  def setUp(self):
    self.longMessage = True

  def testLoadWrongDirRaiseException(self):
    with self.assertRaises(ValueError):
      driver = usgs_pop.UsgsPopDriver(
          os.path.join(TESTDATA_DIR, 'UNKNOWN_DIR'))

  def testReadDataOk(self):
    driver = usgs_pop.UsgsPopDriver(TESTDATA_DIR)
    driver.LoadRaster()
    latitudes = [37.702042, 37.721747, 37.722372]
    longitudes = [-122.414730, -122.391210, -122.395741]
    exp_values = [12686, 2500, 11359]

    densities = driver.GetPopulationDensity(
        latitudes, longitudes)
    self.assertTrue(np.all(densities == exp_values),
                    'Different densities read')

  def testReadBlockDataOk(self):
    driver = usgs_pop.UsgsPopDriver(TESTDATA_DIR)
    driver.LoadRaster((37.7, -122.42, 37.73, -122.35))
    latitudes = [37.702042, 37.721747, 37.722372]
    longitudes = [-122.414730, -122.391210, -122.395741]
    exp_values = [12686, 2500, 11359]
    densities = driver.GetPopulationDensity(
        latitudes, longitudes)
    self.assertTrue(np.all(densities == exp_values),
                    'Different densities read')

  def testLazyReadDataOk(self):
    driver = usgs_pop.UsgsPopDriver(TESTDATA_DIR, lazy_load=True)
    latitudes = [37.702042, 37.721747, 37.722372]
    longitudes = [-122.414730, -122.391210, -122.395741]
    exp_values = [12686, 2500, 11359]
    densities = driver.GetPopulationDensity(
        latitudes, longitudes)
    self.assertTrue(np.all(densities == exp_values),
                    'Different densities read')


if __name__ == '__main__':
  unittest.main()
