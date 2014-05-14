import sys
from setuptools import find_packages, setup
from pip.req import parse_requirements

install_reqs = parse_requirements("requirements.txt")
reqs = [str(ir.req) for ir in install_reqs]
req_links = [str(ir.url) for ir in install_reqs]

if sys.version_info < (2, 7, 0) or sys.version_info >= (3, 0, 0):
    print "Python 2.7 required"

setup(name="disambiguator",
      version="0.1",
      description="Unsupervised word sense disambiguation",
      author="Derek Schultz",
      author_email='derek@derekschultz.net',
      platforms=["any"],
      license="MIT",
      url="https://github.com/daniel-bulger/word-sense-disambiguator",
      packages=find_packages(),
      dependency_links=req_links,
      scripts=["disambiguator/bin/disambiguate"],
      )
