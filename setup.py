from setuptools import setup

with open("README.md", 'r', encoding='utf-8"') as fh:
    outer_long_description = fh.read()

setup(
    name='TDXLib',
    description='a python library for interacting with the TeamDynamix Web API',
    version='0.5.3',
    author='Nat Biggs, Stephen Gaines, Josiah Lansford',
    author_email='tdxlib@cedarville.edu',
    packages=['tdxlib'],
    url='https://github.com/cedarville-university/tdxlib',
    license='GNU General Public License v3.0',
    long_description_content_type='text/markdown',
    long_description=outer_long_description,
    install_requires=['python-dateutil','requests', 'PYjwt'],
    python_requires='>=3.6'
)
