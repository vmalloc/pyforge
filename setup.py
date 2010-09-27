from distutils.core import setup

from forge import __version__ as VERSION

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
      version=VERSION,
      packages=["forge"]
      )
