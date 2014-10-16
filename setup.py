import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='mongoenginelite',
    version='1.0',
    packages=find_packages(),

    # Dependencies
    install_requires = ['mongoengine>=0.8.7'],

    # Metadata for PyPI
    author='Laura Manzur',
    author_email='lc.manzur@novcat.com.co',
    maintainer='Laura Manzur',
    maintainer_email='lc.manzur@novcat.com.co',
    description='This is a lite version of MongoEngine ORM that persists the information in a JSON file, similar to SQLite to SQL databases',
    long_description=README,
    license='Apache License',
    url='https://github.com/lmanzurv/mongo_engine_lite',
    keywords='mongo mongoengine lite',
    download_url='https://github.com/lmanzurv/mongo_engine_lite',
    bugtrack_url='https://github.com/lmanzurv/mongo_engine_lite/issues',
    classifiers=[
        'License :: OSI Approved :: Academic Free License (AFL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7'
    ]
)
