#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name='django-hintcomments',
    version='0.0.2',
    author='Adam Kalinski',
    author_email='adamkalinski@gmail.com',
    url='http://github.com/code22',
    description = 'Ajax support for django comments framework',
    packages=find_packages(),
    provides=['hintcomments'],
    classifiers=[
        'Framework :: Django',
        #'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)