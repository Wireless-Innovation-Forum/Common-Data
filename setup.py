import sys
from distutils.sysconfig import get_config_vars

from setuptools import Extension, setup


def _remove_strict_prototypes():
  """Remove a C-only compiler flag that distutils can add for C++ builds."""
  cfg_vars = get_config_vars()
  for key, value in cfg_vars.items():
    if isinstance(value, str):
      cfg_vars[key] = value.replace("-Wstrict-prototypes", "")


def _compile_args():
  args = ["-D_hypot=hypot"]
  if sys.platform != "win32":
    args.append("-std=c++11")
  return args


_remove_strict_prototypes()

setup(
    ext_modules=[
        Extension(
            "winnf.propag.itm.itm_its",
            sources=[
                "src/winnf/propag/itm/its/itm.cpp",
                "src/winnf/propag/itm/itm_its_py.cpp",
            ],
            include_dirs=["src/winnf/propag/itm/its"],
            extra_compile_args=_compile_args(),
        ),
        Extension(
            "winnf.propag.ehata.ehata_its",
            sources=[
                "src/winnf/propag/ehata/its/ExtendedHata.cpp",
                "src/winnf/propag/ehata/its/FindHorizons.cpp",
                "src/winnf/propag/ehata/its/FindQuantile.cpp",
                "src/winnf/propag/ehata/its/FineRollingHillyTerrainCorectionFactor.cpp",
                "src/winnf/propag/ehata/its/GeneralSlopeCorrectionFactor.cpp",
                "src/winnf/propag/ehata/its/IsolatedRidgeCorrectionFactor.cpp",
                "src/winnf/propag/ehata/its/LeastSquares.cpp",
                "src/winnf/propag/ehata/its/MedianBasicPropLoss.cpp",
                "src/winnf/propag/ehata/its/MedianRollingHillyTerrainCorrectionFactor.cpp",
                "src/winnf/propag/ehata/its/MixedPathCorrectionFactor.cpp",
                "src/winnf/propag/ehata/its/PreprocessTerrainPath.cpp",
                "src/winnf/propag/ehata/ehata_its_py.cpp",
            ],
            include_dirs=["src/winnf/propag/ehata/its"],
            extra_compile_args=_compile_args(),
        ),
    ]
)
