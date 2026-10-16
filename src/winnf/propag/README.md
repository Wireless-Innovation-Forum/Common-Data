# Winnforum propagation models

This folder holds the Winnforum-approved propagation models, currently:
 - `itm`: The ITM (Longley-Rice) model
 - `ehata`: The NTIA Extended-Hata model
 
These implementations are derived from the original ITS/NTIA C++ source code
with minimal modifications when required.

They are wrapped as python extension modules and these models needs to be compiled.

## Building the extensions

Both extensions are built automatically by the repository-root PEP 517 package
build. Python 3.11–3.15 and a C++11 compiler are supported. Use GCC on Linux,
Clang on macOS, or the Microsoft Visual C++ Build Tools on Windows.

From the Common-Data repository root:

```sh
uv sync --locked --extra test
uv run --locked --extra test python -m unittest tests.propag.itm.test_itm tests.propag.ehata.test_ehata
uv build
```

For existing workflows that compile a single extension in place, activate the
repository's Python environment first. The nested setuptools entry points then
work inside their respective extension directories:

```sh
python setup.py build_ext --inplace
```

Install setuptools in that Python environment before using the manual entry
points. Python removed the standard-library `distutils` package in version
3.12; these entry points use setuptools and `sysconfig`.
