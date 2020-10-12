from setuptools import setup

setup(
    name='TDXLib',
    description='a python library for interacting with the TeamDynamix Web API',
    version='0.2.10',
    author='Nat Biggs, Stephen Gaines, Josiah Lansford',
    author_email='tdxlib@cedarville.edu',
    packages=['tdxlib'],
    url='https://github.com/cedarville-university/tdxlib',
    license='GNU General Public License v3.0',
    long_description='This module provides options for programmatically affecting TDX objects, including tickets, '
                     'people, accounts, assets, and groups. Documentation at https://tdxlib.readthedocs.io',
    install_requires=['python-dateutil','requests', 'PYjwt'],
    python_requires='>=3.6'
)
