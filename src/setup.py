import sys
from setuptools import setup, find_packages

ext = 'pyd' if sys.platform == 'win32' else 'so'

setup(name='winnf',
      version='1.0',
      description='Winnforum Commons',
      author='Winnforum Authors',
      license='Apache 2.0',
      python_requires='>=3.7',
      packages=find_packages(),
      #exclude=['*_test.py']),
      #include_package_data=True,  # Not working for some reason
      # TODO(sbdt): review the extended data inclusion method (including C ext).
      package_data={
          '': ['LICENSE', '*.md'],
          'winnf': [
              'propag/itm/itm_it*.%s' % ext,
              'propag/ehata/ehata_it*.%s' % ext
          ],
      },
      install_requires=[
          'numpy',
          'pykml',
          'shapely',
          'six',
      ],
      zip_safe=False)
