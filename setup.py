from distutils.core import setup

setup(
    name='TDXLib',
    description='a python library for interacting with the TeamDynamix Web API',
    version='0.1.3',
    packages=['tdxlib'],
    url='https://github.com/cedarville-university/tdxlib',
    license='GNU General Public License v3.0',
    long_description=open('README.md').read(),
    install_requires=['python-dateutil','requests'],
    python_requires='>=3.6'
)