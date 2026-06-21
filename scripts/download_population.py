"""Download USGS block-level population density rasters from ScienceBase."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

try:
  from sciencebasepy import SbSession
except ModuleNotFoundError as err:
  if err.name != "sciencebasepy":
    raise
  raise SystemExit(
      "sciencebasepy is required to download population data. "
      "Run `uv sync` or install `sciencebasepy`.") from err


SCIENCEBASE_DOI = "doi:10.5066/F74J0C6M"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESTINATION = PROJECT_ROOT / "data" / "pop"
POPULATION_FILE_RE = re.compile(r"^pden(?P<year>\d{4})_block\.zip$")


def _sciencebase_item_for_doi(session, doi):
  identifier = json.dumps({"type": "DOI", "key": doi}, separators=(",", ":"))
  results = session.find_items({
      "q": "",
      "filter": f"itemIdentifier={identifier}",
      "format": "json",
      "max": 2,
  })
  items = results.get("items", [])
  if not items:
    raise SystemExit(f"No ScienceBase item was found for DOI {doi}.")
  if len(items) > 1:
    raise SystemExit(f"Multiple ScienceBase items were found for DOI {doi}.")
  return session.get_item(items[0]["id"])


def _population_files(item):
  files = {}
  for file_info in item.get("files", []):
    match = POPULATION_FILE_RE.match(file_info.get("name", ""))
    if match:
      files[int(match.group("year"))] = file_info
  return dict(sorted(files.items()))


def _format_size(size_bytes):
  if size_bytes is None:
    return "unknown size"
  size = float(size_bytes)
  for unit in ("B", "KB", "MB", "GB"):
    if size < 1024 or unit == "GB":
      return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
    size /= 1024
  return f"{size_bytes} B"


def _safe_extract(zip_path, destination):
  destination = destination.resolve()
  with zipfile.ZipFile(zip_path) as archive:
    for member in archive.infolist():
      target = (destination / member.filename).resolve()
      if destination != target and destination not in target.parents:
        raise ValueError(f"Refusing to extract unsafe path: {member.filename}")
    archive.extractall(destination)


def _print_available(files):
  print("Available population raster years:")
  for year, file_info in files.items():
    print(
        f"  {year}: {file_info['name']} "
        f"({_format_size(file_info.get('size'))})")
  print("\nDownload example:")
  print("  uv run python scripts/download_population.py 2010")


def _existing_file_is_complete(path, expected_size):
  return (
      path.exists()
      and expected_size is not None
      and path.stat().st_size == expected_size
  )


def parse_args():
  parser = argparse.ArgumentParser(
      description=(
          "Download USGS block-level population density rasters from "
          "ScienceBase. With no year argument, list available years."),
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
      "year",
      nargs="?",
      type=int,
      help="Population raster year to download, for example 2010.")
  parser.add_argument(
      "--destination",
      default=DEFAULT_DESTINATION,
      type=Path,
      help=(
          "Directory where the zip file and extracted folder are written. "
          "The default keeps population data under data/pop."))
  parser.add_argument(
      "--no-extract",
      action="store_true",
      help="Download the zip file but do not extract it.")
  parser.add_argument(
      "--force",
      action="store_true",
      help="Download again even if the expected zip file already exists.")
  parser.add_argument(
      "--no-progress",
      action="store_true",
      help="Disable sciencebasepy's download progress indicator.")
  parser.add_argument(
      "--doi",
      default=SCIENCEBASE_DOI,
      help="ScienceBase item DOI to query for population raster files.")
  parser.add_argument(
      "--item-id",
      default=None,
      help=argparse.SUPPRESS)
  return parser.parse_args()


def main():
  args = parse_args()

  session = SbSession()
  if args.item_id:
    item = session.get_item(args.item_id)
    item_source = f"ScienceBase item {args.item_id}"
  else:
    item = _sciencebase_item_for_doi(session, args.doi)
    item_source = f"ScienceBase DOI {args.doi}"
  files = _population_files(item)

  if not files:
    raise SystemExit(
        f"No population raster zip files were found for {item_source}.")

  if args.year is None:
    _print_available(files)
    return 0

  if args.year not in files:
    print(f"Population raster year {args.year} is not available.\n")
    _print_available(files)
    return 2

  file_info = files[args.year]
  destination = args.destination
  destination.mkdir(parents=True, exist_ok=True)
  zip_path = destination / file_info["name"]
  expected_size = file_info.get("size")

  if not args.force and _existing_file_is_complete(zip_path, expected_size):
    print(f"{zip_path} already exists with the expected size.")
  else:
    print(f"Downloading {file_info['name']} to {destination}")
    session.download_file(
        file_info["url"],
        file_info["name"],
        destination=str(destination),
        progress_bar=not args.no_progress,
    )

  if not args.no_extract:
    print(f"Extracting {zip_path} to {destination}")
    _safe_extract(zip_path, destination)

  print(f"Done. Population data for {args.year} are in {destination}.")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
