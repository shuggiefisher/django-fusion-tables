# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-jamboree',
    packages=find_packages(),
    version='0.1',
    author='Robert Kyle',
    author_email='rob@socket2em.com',
    url='http://github.com/shuggiefisher/django-jamboree',
    description="Export django models to google fusion tables",
    long_description=open('README.rst').read(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "python-fusiontables",
    ],
    dependency_links = [
        'http://github.com/shuggiefisher/python-fusiontables/tarball/master#egg=python-fusiontables',
    ]
)
