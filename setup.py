# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()


setup(
    name='coma2',
    version='0.1.0',
    description='CocktailMachine V2 Backend',
    long_description=readme,
    author='Fabian Geyer',
    author_email='fbn.geyer@gmail.com',
    url='https://github.com/Fabian-Geyer/coma2-backend.git',
    packages=find_packages(exclude=('tests', 'docs'))
)
