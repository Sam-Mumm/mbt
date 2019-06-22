from setuptools import setup, find_packages

setup(
    name = 'mbt',
    version = '0.1',
    url = 'https://github.com/Sam-Mumm/mbt.git',
    author = 'Dan',
    author_email = 'dan.steffen.de@gmail.com',
    description = 'My Bug Tracker',
    packages = find_packages(),
    install_requires = ['tabulate==0.8.3']