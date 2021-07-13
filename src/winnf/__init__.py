import os

# Management of geo database location
_ZONES_DIR = None
_NED_DIR = None
_NLCD_DIR = None
_COUNTY_DIR = None
_POP_DIR = None


def SetGeoBaseDir(directory):
  SetZonesDir(os.path.join(directory, 'zones'))
  SetNedDir(os.path.join(directory, 'ned'))
  SetNlcdDir(os.path.join(directory, 'nlcd'))
  SetCountyDir(os.path.join(directory, 'counties'))
  SetPopDir(os.path.join(directory, 'pop'))

def SetZonesDir(directory):
  global _ZONES_DIR
  _ZONES_DIR = directory

def SetNedDir(directory):
  global _NED_DIR
  _NED_DIR = directory

def SetNlcdDir(directory):
  global _NLCD_DIR
  _NLCD_DIR = directory

def SetCountyDir(directory):
  global _COUNTY_DIR
  _COUNTY_DIR = directory

def SetPopDir(directory):
  global _POP_DIR
  _POP_DIR = directory


def GetZonesDir():
  return _ZONES_DIR

def GetNedDir():
  return _NED_DIR

def GetNlcdDir():
  return _NLCD_DIR

def GetCountyDir():
  return _COUNTY_DIR

def GetPopDir():
  return _POP_DIR
