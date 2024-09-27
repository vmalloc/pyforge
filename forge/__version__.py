import sys
if sys.version_info < (3, 8):
   import pkg_resources
   get_distribution = pkg_resources.get_distribution
else:
   from importlib.metadata import distribution
   get_distribution = distribution

__version__ = get_distribution('pyforge').version
