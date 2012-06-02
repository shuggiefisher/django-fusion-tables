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
    long_description=open('README.txt').read(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "git+git://github.com/shuggiefisher/python-fusiontables.git",
    ],
)
