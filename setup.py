import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "forge", "__version__.py")) as version_file:
    exec(version_file.read())

setup(name="pyforge",
      classifiers = [
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python :: 2.6",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Software Development :: Testing",
          ],
      description="Python mocking framework",
      license="BSD",
      author="Rotem Yaari",
      author_email="vmalloc@gmail.com",
      url="http://github.com/vmalloc/pyforge",
      version=__version__,
      install_requires=['sentinels'],
      packages=find_packages(exclude=["tests"])
      )
