from setuptools import setup

setup(name='selenium',
      version='1.0',
      packages=['selenium'],
      url='',
      license='GNU GPLv3',
      install_require=['numpy', 'scipy', 'tables', 'pandas', 'pvlib', 'pytz', 'matplotlib'],
      author='Don Walker',
      author_email='don.walker@aero.org',
      description='python package to work up Selenium and AMU data.  Can  be used to apply atmospheric corrections to solar cell data')