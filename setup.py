#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'pandas>=0.19.0',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pyrefine',
    version='0.1.0',
    description="Execute OpenRefine JSON scripts without OpenRefine (or Java).",
    long_description=readme + '\n\n' + history,
    author="Jez Cope",
    author_email='j.cope@erambler.co.uk',
    url='https://github.com/jezcope/pyrefine',
    packages=[
        'pyrefine',
    ],
    package_dir={'pyrefine':
                 'pyrefine'},
    entry_points={
        'console_scripts': [
            'pyrefine=pyrefine.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='pyrefine',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
