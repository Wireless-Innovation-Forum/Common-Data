"""Compatibility entry point for the repository-root setuptools build.

Install Common-Data from its repository root. Legacy callers of src/setup.py
still get the same package metadata and compiled propagation extensions.
"""

import os
from pathlib import Path
import runpy


project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
runpy.run_path(str(project_root / "setup.py"), run_name="__main__")
