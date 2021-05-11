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

"""Zones library.

Allows to retrieve some common geographical zones. Currently:
 - US/Canadian border.
 - US overall Border
 - US Urban areas

Typical usage:

  # Get the US/Canada border as a shapely |MultiLineString|.
  us_ca_border = GetUsCanadaBorder()

  # Get the US border as a shapely |MultiPolygon|.
  us_border = GetUsBorder()

  # Get the US urban areas as a simplified shapely |GeometryCollection|.
  urban_areas = GetUrbanAreas()

"""
import os
import zipfile

from pykml import parser
import shapely.geometry as sgeo
import shapely.ops as ops

import winnf

# The reference files for extra zones.
USBORDER_FILE = 'usborder.kmz'
URBAN_AREAS_FILE = 'Urban_Areas_3601.kmz'
USCANADA_BORDER_FILE = 'uscabdry_sampled.kmz'


# Pointers to the data
_border_zone = None
_uscanada_border = None



def _SplitCoordinates(coord):
  """Returns lon,lat from 'coord', a KML coordinate string field."""
  lon, lat, _ = coord.strip().split(',')
  return float(lon), float(lat)


def _GetPoint(point):
  """Gets a Point from a placemark."""
  coord = point.coordinates.text.strip()
  return sgeo.Point(_SplitCoordinates(coord))


def _GetPolygon(poly):
  """Returns a |shapely.geometry.Polygon| from a KML 'Polygon' element."""
  out_ring = poly.outerBoundaryIs.LinearRing.coordinates.text.strip().split(' ')
  out_points = [_SplitCoordinates(coord) for coord in out_ring]
  int_points = []
  try:
    for inner_boundary in poly.innerBoundaryIs:
      inner_ring = inner_boundary.LinearRing.coordinates.text.strip().split(' ')
      int_points.append([_SplitCoordinates(coord) for coord in inner_ring])
  except AttributeError:
    pass
  return sgeo.Polygon(out_points, holes=int_points)


def _GetLineString(linestring):
  """Returns a |shapely.geometry.LineString| from a KML 'LineString' element."""
  coords = linestring.coordinates.text.strip().split(' ')
  points = [_SplitCoordinates(coord) for coord in coords]
  return sgeo.LineString(points)


# A private struct for configurable zone with geometry and attributes
class _Zone:
  """A simplistic struct holder for zones."""
  def __init__(self, fields):
    """Initializes attributes to None for a list of `fields`."""
    self.fields = fields
    for field in fields:
      setattr(self, field, None)

  def __repr__(self):
    """Return zone representation."""
    return 'Zone(geometry=%s, %s)' % (
        'None' if not hasattr(self, 'geometry') else self.geometry.type,
        ', '.join(['%s=%s' % (attr, getattr(self, attr)) for attr in self.fields]))


def ReadKmlZones(kml_path, root_id_zone='Placemark', ignore_if_parent=None,
                  data_fields=None, simplify=0, fix_invalid=True):
  """Gets all the zones defined in a KML.

  This assumes that each zone is either a bunch of polygons, or a bunch of points.

  Args:
    kml_path: The path name to the exclusion zone KML or KMZ.
    root_id_zone: The root id defininig a zone. Usually it is 'Placemark'.
    data_fields: List of string defining the data fields to extract from the KML
      'ExtendedData'. If None, nothing is extracted.
    simplify: If set, simplifies the resulting polygons.
    fix_invalid: If True, try to fix invalid DPA zone (using buffer(0) trick).

  Returns:
    A dictionary of elements keyed by their name, with each elements being:
      - if no data_fields requested:  a |shapely| Polygon/MultiPolygon or Point/MultiPoint
      - if data_fields requested:
        a struct with attributes:
          * 'geometry': a |shapely| Polygon/MultiPolygon or Point/MultiPoint
          * the requested data_fields as attributes. The value are string, or None
            if the data fields is unset in the KML. If several identical data_fields are
            found, they are put in a list.
  """
  if kml_path.endswith('kmz'):
    with zipfile.ZipFile(kml_path) as kmz:
      kml_name = [info.filename for info in kmz.infolist()
                  if os.path.splitext(info.filename)[1] == '.kml'][0]
      with kmz.open(kml_name) as kml_file:
        root = parser.parse(kml_file).getroot()
  else:
    with open(kml_path, 'rb') as kml_file:
      root = parser.parse(kml_file).getroot()
  tag = root.tag[:root.tag.rfind('}')+1]
  zones = {}
  for element in root.findall('.//' + tag + root_id_zone):
    # Ignore nested root_id within root_id
    if element.find('.//' + tag + root_id_zone) is not None:
      continue
    if ignore_if_parent is not None and element.getparent().tag.endswith(ignore_if_parent):
      continue

    name = element.name.text
    # Read the zone geometry
    geometry = None
    polygons = [_GetPolygon(poly)
                for poly in element.findall('.//' + tag + 'Polygon')]
    if polygons:
      if len(polygons) == 1:
        polygon = polygons[0]
      else:
        polygon = sgeo.MultiPolygon(polygons)
      # Fix most invalid polygons
      if fix_invalid:
        polygon = polygon.buffer(0)
      if simplify:
        polygon.simplify(simplify)
      if not polygon.is_valid:
        # polygon is broken and should be fixed upstream
        raise ValueError('Polygon %s is invalid and cannot be cured.' % name)
      geometry = polygon
    else:
      points = [_GetPoint(point)
                for point in element.findall('.//' + tag + 'Point')]
      geometry = ops.unary_union(points)

    # Read the data_fields
    if data_fields is None:
      zones[name] = geometry
    else:
      zone = _Zone(data_fields)
      zone.geometry = geometry
      data_fields_lower = [field.lower() for field in data_fields]
      zones[name] = zone
      ext_data = element.ExtendedData.getchildren()
      for data in ext_data:
        data_attrib = data.attrib['name']
        data_value = str(data.value)
        if data_attrib.lower() in data_fields_lower:
          if getattr(zone, data_attrib, None) is None:
            setattr(zone, data_attrib, data_value)
          else:
            existing_data = getattr(zone, data_attrib)
            try:
              existing_data.append(str(data_value))
              setattr(zone, data_attrib, existing_data)
            except:
              setattr(zone, data_attrib, [existing_data, str(data_value)])
  return zones


def ReadKmlBorder(kml_path, root_id='Placemark'):
  """Gets the border defined in a KML.

  Args:
    kml_path: The path name to the border file KML or KMZ.
    root_id_zone: The root id defininig a zone. Usually it is 'Placemark'.

  Returns:
    A dictionary of |shapely| LineString keyed by their names.
  """
  if kml_path.endswith('kmz'):
    with zipfile.ZipFile(kml_path) as kmz:
      kml_name = [info.filename for info in kmz.infolist()
                  if os.path.splitext(info.filename)[1] == '.kml'][0]
      with kmz.open(kml_name) as kml_file:
        root = parser.parse(kml_file).getroot()
  else:
    with open(kml_path, 'rb') as kml_file:
      root = parser.parse(kml_file).getroot()

  tag = root.tag[:root.tag.rfind('}') + 1]
  linetrings_dict = {}
  for element in root.findall('.//' + tag + root_id):
    # Ignore nested root_id within root_id
    if element.find('.//' + tag + root_id) is not None:
      continue
    name = element.name.text
    linestrings = [
        _GetLineString(l)
        for l in element.findall('.//' + tag + 'LineString')
    ]
    if not linestrings:
      continue
    if len(linestrings) == 1:
      linestring = linestrings[0]
    else:
      linestring = sgeo.MultiLineString(linestrings)

    linetrings_dict[name] = linestring

  return linetrings_dict


def GetUsCanadaBorder():
  """Gets the US/Canada border as a |shapely.MultiLineString|."""
  global _uscanada_border
  if _uscanada_border is None:
    kml_file = os.path.join(winnf.GetZonesDir(), USCANADA_BORDER_FILE)
    lines = ReadKmlBorder(kml_file)
    _uscanada_border = ops.unary_union(list(lines.values()))
  return _uscanada_border


def GetUsBorder():
  """Gets the US border as a |shapely.MultiPolygon|.

  This is a composite US border for simulation purposes only.
  """
  global _border_zone
  if _border_zone is None:
    kml_file = os.path.join(winnf.GetZonesDir(), USBORDER_FILE)
    zones = ReadKmlZones(kml_file)
    _border_zone = ops.unary_union(list(zones.values()))
  return _border_zone


def GetUrbanAreas(simplify_deg=1e-3):
  """Gets the US urban area as a |shapely.GeometryCollection|.

  Note: Client code should cache it as expensive to load (and not cached here).

  Args:
    simplify_deg: if defined, simplify the zone with given tolerance (degrees).
      Default is 1e-3 which corresponds roughly to 100m in continental US.
  """
  kml_file = os.path.join(winnf.GetZonesDir(), URBAN_AREAS_FILE)
  zones = ReadKmlZones(kml_file, root_id_zone='Document', simplify=simplify_deg)
  urban_areas = sgeo.GeometryCollection(list(zones.values()))  # ops.unary_union(list(zones.values()))
  return urban_areas
