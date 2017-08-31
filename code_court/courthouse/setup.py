from setuptools import setup, find_packages

from os import path

SCRIPT_DIR = path.dirname(path.realpath(__file__))

with open(path.join(SCRIPT_DIR, 'requirements.txt')) as f:
    requirements = f.read().splitlines()

setup(
    name='code_court',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements)
