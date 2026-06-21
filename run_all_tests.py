"""Run the Common-Data unit tests from any platform."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
TEST_DIR = PROJECT_ROOT / "tests"
GDAL_SKIP_REASON = "GDAL/osgeo is not installed"


def _print_optional_dependency_skips(result: unittest.TestResult) -> None:
  gdal_skips = [
      test
      for test, reason in result.skipped
      if reason == GDAL_SKIP_REASON
  ]
  if not gdal_skips:
    return

  test_word = "test was" if len(gdal_skips) == 1 else "tests were"
  print(
      "\nNote: "
      f"{len(gdal_skips)} population raster {test_word} skipped because "
      "GDAL/osgeo is optional and is not installed. "
      "Install it with `uv sync --extra pop` to enable these tests.",
      file=sys.stderr,
  )


def main() -> int:
  sys.path.insert(0, str(SRC_DIR))

  suite = unittest.defaultTestLoader.discover(
      start_dir=str(TEST_DIR),
      pattern="test_*.py",
      top_level_dir=str(PROJECT_ROOT),
  )
  result = unittest.TextTestRunner(verbosity=1).run(suite)
  _print_optional_dependency_skips(result)
  return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
  raise SystemExit(main())
