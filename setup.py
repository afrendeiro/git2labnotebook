#! /usr/bin/env python

import sys

# take care of extra required modules depending on Python version
extra = {}

try:
    from setuptools import setup
    if sys.version_info < (2, 7):
        extra['install_requires'] = ['argparse']
    if sys.version_info >= (3,):
        extra['use_2to3'] = True
except ImportError:
    from distutils.core import setup
    if sys.version_info < (2, 7):
        extra['dependencies'] = ['argparse']


with open("VERSION", 'r') as versionfile:
    version = versionfile.read().strip()

# setup
setup(
    name="git2labnotebook",
    packages=["git2labnotebook"],
    version=version,
    description="",
    long_description=open('README.md').read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python :: 2.7"
    ],
    keywords="notebook, git, markdown",
    url="https://github.com/afrendeiro/git2labnotebook",
    author=u"Andre Rendeiro",
    license="GPL2",
    install_requires=["pandas", "gitpython"],
    entry_points={
        "console_scripts": [
            'git2labnotebook = git2labnotebook.git2labnotebook:main'
        ],
    },
    **extra
)
