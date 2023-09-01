#!/usr/bin/env python

from setuptools import setup, find_packages

from sseclient.version import name, version

with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name=name,
    version=version,
    author='Maxime Petazzoni',
    author_email='maxime.petazzoni@bulix.org',
    description='SSE client for Python',
    license='Apache Software License v2',
    long_description=long_description,
    zip_safe=True,
    packages=find_packages(),
    package_data={'sseclient': ['py.typed', '*.pyi']},
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    url='https://github.com/mpetazzoni/sseclient',
)
