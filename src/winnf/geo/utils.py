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
#
# Modified in 2019 by Serge Barbosa Da Torre - Google LLC
#  - provides only required routines for fcc_cov

"""Utility geometry routines.
"""
import json

import numpy as np
import shapely.geometry as sgeo
import shapely.ops as ops
from shapely import affinity

import six


# Earth ellipsoidal parameters.
_EARTH_MEAN_RADIUS_KM = 6371.0088  # By IUGG
_WGS_EQUATORIAL_RADIUS_KM2 = 6378.137
_WGS_POLAR_RADIUS_KM2 = 6356.753
_EQUATORIAL_DIST_PER_DEGREE = 2 * np.pi * _WGS_EQUATORIAL_RADIUS_KM2 / 360
_POLAR_DIST_PER_DEGREE = 2 * np.pi * _WGS_POLAR_RADIUS_KM2 / 360


def HasCorrectGeoJsonWinding(geometry):
  """Returns True if a GeoJSON geometry has correct windings.

  A GeoJSON polygon should follow the right-hand rule with respect to the area it
  bounds, ie exterior rings are CCW and holes are CW.

  Args:
    geometry: A dict or string representing a GeoJSON geometry.

  Raises:
    ValueError: If invalid input or GeoJSON geometry type.
  """
  if isinstance(geometry, six.string_types):
    geometry = json.loads(geometry)
  if not isinstance(geometry, dict) or 'type' not in geometry:
    raise ValueError('Invalid GeoJSON geometry.')

  def _HasSinglePolygonCorrectWinding(coords):
    exterior = coords[0]
    if not sgeo.LinearRing(exterior).is_ccw:
      return False
    for hole in coords[1:]:
      if sgeo.LinearRing(hole).is_ccw:
        return False
    return True

  if geometry['type'] == 'Polygon':
    coords = geometry['coordinates']
    return _HasSinglePolygonCorrectWinding(coords)
  elif geometry['type'] == 'MultiPolygon':
    for coords in geometry['coordinates']:
      if not _HasSinglePolygonCorrectWinding(coords):
        return False
    return True
  elif geometry['type'] == 'GeometryCollection':
    for subgeo in geometry['geometries']:
      if not HasCorrectGeoJsonWinding(subgeo):
        return False
    return True
  else:
    return True


def InsureGeoJsonWinding(geometry):
  """Returns the input GeoJSON geometry with windings corrected.

  A GeoJSON polygon should follow the right-hand rule with respect to the area it
  bounds, ie exterior rings are CCW and holes are CW.
  Note that the input geometry may be modified in place (case of a dict).

  Args:
    geometry: A dict or string representing a GeoJSON geometry. The returned
      corrected geometry is in same format as the input (dict or str).

  Raises:
    ValueError: If invalid input or GeoJSON geometry type.
  """
  if HasCorrectGeoJsonWinding(geometry):
    return geometry

  is_str = False
  if isinstance(geometry, six.string_types):
    geometry = json.loads(geometry)
    is_str = True
  if not isinstance(geometry, dict) or 'type' not in geometry:
    raise ValueError('Invalid GeoJSON geometry.')

  def _InsureSinglePolygonCorrectWinding(coords):
    """Modifies in place the coords for correct windings."""
    exterior = coords[0]
    if not sgeo.LinearRing(exterior).is_ccw:
      exterior.reverse()
    for hole in coords[1:]:
      if sgeo.LinearRing(hole).is_ccw:
        hole.reverse()

  def _list_convert(x):
    # shapely mapping returns a nested tuple.
    return [_list_convert(xx) for xx in x] if isinstance(x, (tuple, list)) else x

  if 'coordinates' in geometry:
    geometry['coordinates'] = _list_convert(geometry['coordinates'])

  if geometry['type'] == 'Polygon':
    _InsureSinglePolygonCorrectWinding(geometry['coordinates'])
  elif geometry['type'] == 'MultiPolygon':
    for coords in geometry['coordinates']:
      _InsureSinglePolygonCorrectWinding(coords)
  elif geometry['type'] == 'GeometryCollection':
    for subgeo in geometry['geometries']:
      InsureGeoJsonWinding(subgeo)

  if is_str:
    geometry = json.dumps(geometry)
  return geometry


def _GeoJsonToShapelyGeometry(geometry):
  """Returns a |shapely| geometry from a GeoJSON geometry.

  Args:
    geometry: A dict or string representing a GeoJSON geometry.

  Raises:
    ValueError: If invalid GeoJSON geometry is passed.
  """
  if isinstance(geometry, six.string_types):
    geometry = json.loads(geometry)
  if not isinstance(geometry, dict) or 'type' not in geometry:
    raise ValueError('Invalid GeoJSON geometry.')

  if 'geometries' in geometry:
    return sgeo.GeometryCollection([_GeoJsonToShapelyGeometry(g)
                                    for g in geometry['geometries']])
  geometry = sgeo.shape(geometry)
  if isinstance(geometry, sgeo.Polygon) or isinstance(geometry, sgeo.MultiPolygon):
    geometry = geometry.buffer(0)
  return geometry


def ToShapely(geometry):
  """Returns a |shapely| geometry from a generic geometry or a GeoJSON.

  The original geometry structure is maintained, for example GeometryCollections
  and MultiPolygons are kept as is. To dissolve them, apply the
  `shapely.ops.unary_union()` routine on the output.

  Args:
    geometry: A generic geometry or a GeoJSON geometry (dict or str). A generic
      geometry is any object implementing the __geo_interface__ supported by all
      major geometry libraries (shapely, ..)
  """
  if isinstance(geometry, sgeo.base.BaseGeometry):
    return geometry
  try:
    return _GeoJsonToShapelyGeometry(geometry.__geo_interface__)
  except AttributeError:
    return _GeoJsonToShapelyGeometry(geometry)


def ToGeoJson(geometry, as_dict=False):
  """Returns a GeoJSON geometry from a generic geometry.

  A generic geometry implements the __geo_interface__ as supported by all major
  geometry libraries, such as shapely, etc...

  Args:
    geometry: A generic geometry, for example a shapely geometry.
    as_dict: If True returns the GeoJSON as a dict, otherwise as a string.
  """
  json_geometry = json.dumps(InsureGeoJsonWinding(geometry.__geo_interface__))
  return json.loads(json_geometry) if as_dict else json_geometry


def InsureFeatureCollection(geometry, as_dict=False):
  """Returns a GeoJSON feature collection from a geojson geometry.

  Args:
    geometry: A geojson geometry, either as dict or str. Can be any type
      of GeoJSON: standard geometry, feature or feature collection.
  """
  if isinstance(geometry, six.string_types):
    geometry = json.loads(geometry)
  if 'type' not in geometry:
    raise ValueError('Invalid GeoJSON geometry.')
  if geometry['type'] == 'FeatureCollection':
    pass
  elif geometry['type'] == 'Feature':
    geometry = {'type': 'FeatureCollection',
                'features': [geometry]}
  else:
    geometry = {'type': 'FeatureCollection',
                'features': [
                    {'type': 'Feature',
                    'properties': {},
                    'geometry': geometry}
                ]
    }
  return geometry if as_dict else json.dumps(geometry)


def PolygonsAlmostEqual(poly_ref, poly, tol_perc=10):
  """Checks similarity of a polygon to a reference polygon within some tolerance.

  Args:
    poly_ref, poly: Two polygons or multipolygons defined  either as shapely,
      GeoJson (dict or str) or generic geometry. A generic geometry is any
      object implementing the __geo_interface__ protocol.

  Returns:
    True if the two polygons are equal (within the tolerance), False otherwise.
  """
  poly_ref = ToShapely(poly_ref)
  poly = ToShapely(poly)
  union_polys = poly_ref.union(poly)
  intersection_polys = poly_ref.intersection(poly)
  return ((GeometryArea(union_polys) - GeometryArea(intersection_polys))
          < tol_perc/100. * GeometryArea(poly_ref))


def _RingArea(latitudes, longitudes):
  """Returns the approximate area of a ring on earth surface (m^2).

  Args:
    latitudes (sequence of float): the latitudes along the ring vertices (degrees).
    longitudes (sequence of float): the longitudes along the ring vertices (degrees).
  """
  # This uses the approximate formula on spheroid derived from:
  #    Robert. G. Chamberlain and William H. Duquette, "Some Algorithms for Polygons on a Sphere",
  #    https://trs-new.jpl.nasa.gov/bitstream/handle/2014/40409/JPL%20Pub%2007-3%20%20w%20Errata.pdf
  #  A small correction is performed to account for the ellipsoi by using both the
  #  the equatorial radius and polar radius.
  if len(latitudes) != len(longitudes):
    raise ValueError('Inconsistent inputs')
  num_coords = len(latitudes)

  if latitudes[0] == latitudes[-1] and longitudes[0] == longitudes[-1]:
    num_coords -= 1
  latitudes = np.radians(latitudes[:num_coords])
  longitudes = np.radians(longitudes[:num_coords])
  if num_coords < 3:
    return 0.

  idx = np.arange(num_coords)
  next = idx + 1
  next[-1] = 0
  prev = idx - 1

  area = np.sum(np.sin(latitudes) * (longitudes[next] - longitudes[prev]))
  area *= 0.5 * _WGS_EQUATORIAL_RADIUS_KM2 * _WGS_POLAR_RADIUS_KM2
  return np.abs(area)


def GeometryArea(geometry, merge_geometries=False):
  """Returns the approximate area of a geometry on earth (in km2).

  This uses the approximate formula on spheroid derived from:
    Robert. G. Chamberlain and William H. Duquette
    "Some Algorithms for Polygons on a Sphere",
    See: https://trs-new.jpl.nasa.gov/bitstream/handle/2014/40409/JPL%20Pub%2007-3%20%20w%20Errata.pdf
  An additional small correction is performed to account partially for the earth
  ellipsoid.

  Args:
    geometry: A geometry defined in WGS84 or NAD83 coordinates (degrees) and
      encoded either as shapely, GeoJson (dict or str) or a generic geometry.
      A generic geometry is any object implementing the __geo_interface__ protocol.
    merge_geometries (bool): If True, then multi geometries will be unioned to
     dissolve intersection prior to the area calculation.

  Returns:
    The approximate area within the geometry (in square kilometers).
  """
  geometry = ToShapely(geometry)
  if (isinstance(geometry, sgeo.Point) or
      isinstance(geometry, sgeo.LineString) or
      isinstance(geometry, sgeo.LinearRing)):
    # Lines, rings and points have null area
    return 0.
  elif isinstance(geometry, sgeo.Polygon):
    return (_RingArea(geometry.exterior.xy[1], geometry.exterior.xy[0])
            - sum(_RingArea(interior.xy[1], interior.xy[0])
                  for interior in geometry.interiors))
  else:
    # Multi geometries
    if merge_geometries:
      geometry = ops.unary_union(geometry)
      # Test if dissolved into a simple geometry.
      try:
        iter(geometry)
      except TypeError:
        return GeometryArea(geometry)
    return sum(GeometryArea(simple_shape) for simple_shape in geometry)


def _ProjectEqc(geometry, ref_latitude=None):
  """Projects a geometry using equirectangular projection.

  Args:
    geometry: A |shapely| geometry with lon,lat coordinates.
    ref_latitude: A reference latitude for the Eqc projection. If None, using
      the centroid of the geometry.
  Returns:
    A tuple of:
      the same geometry in equirectangular projection.
      the reference latitude parameter used for the equirectangular projection.
  """
  if ref_latitude is None:
    ref_latitude = geometry.centroid.y
  geometry = affinity.affine_transform(
      geometry,
      (_EQUATORIAL_DIST_PER_DEGREE * np.cos(np.radians(ref_latitude)), 0.0,
       0.0, _POLAR_DIST_PER_DEGREE,
       0, 0))
  return geometry, ref_latitude


def _InvProjectEqc(geometry, ref_latitude):
  """Returns the inverse equirectangular projection of a geometry.

  Args:
    geometry: A |shapely| geometry with lon,lat coordinates.
    ref_latitude: The reference latitude of the equirectangular projection.
  """
  geometry = affinity.affine_transform(
      geometry,
      (1./(_EQUATORIAL_DIST_PER_DEGREE * np.cos(np.radians(ref_latitude))), 0.0,
       0.0, 1./_POLAR_DIST_PER_DEGREE,
       0, 0))
  return geometry


def Buffer(geometry, distance_km, ref_latitude=None, **kwargs):
  """Returns a geometry with an enveloppe at a given distance (in km).

  This uses the traditional shapely `buffer` method but on the reprojected
  geometry. As such this is somewhat approximate depending on the size of the
  geometry and the buffering distance.

  Args:
    geometry: A |shapely| or geojson geometry.
    distance_km: The buffering distance in km.
    ref_latitude: A reference latitude for the Eqc projection. If None, using
      the centroid of the geometry.
    **kwargs: The optional parameters forwarded to the shapely `buffer` routine:
      (for example: resolution, cap_style, join_style)
  """
  geom = ToShapely(geometry)
  proj_geom, ref_latitude = _ProjectEqc(geom, ref_latitude)
  proj_geom = proj_geom.buffer(distance_km, **kwargs)
  geom = _InvProjectEqc(proj_geom, ref_latitude)
  if isinstance(geometry, sgeo.base.BaseGeometry):
    return geom
  else:
    return ToGeoJson(geom, as_dict=isinstance(geometry, dict))


def GridPolygon(poly, res_arcsec):
  """Grids a polygon or multi-polygon.

  This performs regular gridding of a polygon in PlateCarree (equirectangular)
  projection (ie with fixed step in degrees in lat/lon space).
  Points falling in the boundary of polygon will be included.

  Args:
    poly: A Polygon or MultiPolygon in WGS84 or NAD83, defined either as a
      shapely, GeoJSON (dict or str) or generic  geometry.
      A generic geometry is any object implementing the __geo_interface__ protocol.
    res_arcsec: The resolution (in arcsec) used for regular gridding.

  Returns:
    A list of (lon, lat) defining the grid points.
  """
  poly = ToShapely(poly)
  bound_area = (poly.bounds[2] - poly.bounds[0]) * (poly.bounds[3] - poly.bounds[1])
  if not poly:
    return []
  if isinstance(poly, sgeo.MultiPolygon) and poly.area < bound_area * 0.01:
    # For largely disjoint polygons, we process per polygon
    # to avoid inefficiencies if polygons largely disjoint.
    pts = ops.unary_union(
        [sgeo.asMultiPoint(GridPolygon(p, res_arcsec))
         for p in poly])
    return [(p.x, p.y) for p in pts]

  res = res_arcsec / 3600.
  bounds = poly.bounds
  lng_min = np.floor(bounds[0] / res) * res
  lat_min = np.floor(bounds[1] / res) * res
  lng_max = np.ceil(bounds[2] / res) * res + res/2
  lat_max = np.ceil(bounds[3] / res) * res + res/2
  # The mesh creation is conceptually equivalent to
  #mesh_lng, mesh_lat = np.mgrid[lng_min:lng_max:res,
  #                              lat_min:lat_max:res]
  # but without the floating point accumulation errors
  mesh_lng, mesh_lat = np.meshgrid(
      np.arange(np.floor((lng_max - lng_min) / res) + 1),
      np.arange(np.floor((lat_max - lat_min) / res) + 1),
      indexing='ij')
  mesh_lng = lng_min + mesh_lng * res
  mesh_lat = lat_min + mesh_lat * res
  points = np.vstack((mesh_lng.ravel(), mesh_lat.ravel())).T
  # Performs slight buffering by 1mm to include border points in case they fall
  # exactly on a multiple of 1 arcsec.
  pts = poly.buffer(1e-8).intersection(sgeo.asMultiPoint(points))
  if not pts:
    return []
  if isinstance(pts, sgeo.Point):
    return [(pts.x, pts.y)]
  return [(p.x, p.y) for p in pts]


def GridPolygonMetric(poly, res_km):
  """Grids a polygon or multi-polygon with approximate resolution (in km).

  This is a replacement of `utils.GridPolygon()` for gridding with
  approximate metric distance on both latitude and longitude directions. The
  regular gridding is still done in PlateCarree (equirectangular) projection,
  but with different steps in degrees in lat and long direction.
  Points falling in the boundary of polygon will be included.

  Args:
    poly: A Polygon or MultiPolygon in WGS84 or NAD83, defined either as a
      shapely, GeoJSON (dict or str) or generic  geometry.
      A generic geometry is any object implementing the __geo_interface__
      protocol.
    res_km: The resolution (in km) used for gridding.

  Returns:
    A list of (lon, lat) defining the grid points.
  """
  poly = ToShapely(poly)
  bound_area = ((poly.bounds[2] - poly.bounds[0]) *
                (poly.bounds[3] - poly.bounds[1]))
  if isinstance(poly, sgeo.MultiPolygon) and poly.area < bound_area * 0.01:
    # For largely disjoint polygons, we process per polygon
    # to avoid inefficiencies if polygons largely disjoint.
    pts = ops.unary_union(
        [sgeo.asMultiPoint(GridPolygonMetric(p, res_km))
         for p in poly])
    return [(p.x, p.y) for p in pts]

  # Note: using as reference the min latitude, ie actual resolution < res_km.
  # This is to match NTIA procedure.
  ref_latitude = poly.bounds[1]  # ref_latitude = poly.centroid.y
  res_lat = res_km / _POLAR_DIST_PER_DEGREE
  res_lng = res_km / (
      _EQUATORIAL_DIST_PER_DEGREE * np.cos(np.radians(ref_latitude)))
  bounds = poly.bounds
  lng_min = np.floor(bounds[0] / res_lng) * res_lng
  lat_min = np.floor(bounds[1] / res_lat) * res_lat
  lng_max = np.ceil(bounds[2] / res_lng) * res_lng + res_lng/2.
  lat_max = np.ceil(bounds[3] / res_lat) * res_lat + res_lat/2.
  # The mesh creation is conceptually equivalent to
  # mesh_lng, mesh_lat = np.mgrid[lng_min:lng_max:res_lng,
  #                               lat_min:lat_max:res_lat]
  # but without the floating point accumulation errors
  mesh_lng, mesh_lat = np.meshgrid(
      np.arange(np.floor((lng_max - lng_min) / res_lng) + 1),
      np.arange(np.floor((lat_max - lat_min) / res_lat) + 1),
      indexing='ij')
  mesh_lng = lng_min + mesh_lng * res_lng
  mesh_lat = lat_min + mesh_lat * res_lat
  points = np.vstack((mesh_lng.ravel(), mesh_lat.ravel())).T
  # Performs slight buffering by 1mm to include border points in case they fall
  # exactly on a multiple of
  pts = poly.buffer(1e-8).intersection(sgeo.asMultiPoint(points))
  if isinstance(pts, sgeo.Point):
    return [(pts.x, pts.y)]
  return [(p.x, p.y) for p in pts]


def SampleLine(line, res_km, ref_latitude=None,
               equal_intervals=False, precision=5, ratio=1.0):
  """Samples a line with approximate resolution (in km).

  Args:
    line: A shapely or GeoJSON |LineString|.
    res_km: The resolution (in km).
    ref_latitude: A reference latitude for the Eqc projection. If None, using
      the centroid of the line.
    equal_intervals: If True, all intervals are equal to finish on the edges.
    precision: Simplify final coordinates with provided precision.
    ratio: Only span the given line length.
  Returns:
    A list of (lon, lat) along the line every `res_km`.
  """
  line = ToShapely(line)
  proj_line, ref_latitude = _ProjectEqc(line, ref_latitude)
  if not equal_intervals:
    points = sgeo.MultiPoint(
        [proj_line.interpolate(dist)
         for dist in np.arange(0, ratio * proj_line.length - 1e-6, res_km)])
  else:
    n_intervals = ratio * proj_line.length // res_km
    points = sgeo.MultiPoint(
        [proj_line.interpolate(dist)
         for dist in np.linspace(0, ratio * proj_line.length, n_intervals)])
  points = _InvProjectEqc(points, ref_latitude)
  return [(round(p.x, precision), round(p.y, precision)) for p in points]
