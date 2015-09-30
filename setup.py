from setuptools import setup
import pip
from pip.req import parse_requirements
from pip.exceptions import InstallationError

try:
    try:
        requirements = parse_requirements("requirements.txt", session=pip.download.PipSession())
    except AttributeError:
        requirements = parse_requirements("requirements.txt")

    install_requires = [str(r.req) for r in requirements]
except InstallationError:
    install_requires = []

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name="went",
    version="0.1.0",
    description="Tools for implementing a webmention enpoint.",
    license="MIT",
    author="Giovanni T. Parra",
    author_email='fiatjaf@gmail.com',
    install_requires=[
        'PyYAML==3.11',
        'beautifulsoup4==4.3.2',
        'gunicorn==19.2.1',
        'html5lib==0.999',
        'mf2py==0.2.4',
        'pyaml==15.02.1',
        'redis==2.10.3',
        'requests==2.5.3',
        'six==1.9.0',
        'wsgiref==0.1.2',
        'html2text==2015.2.18'
    ],
    long_description=long_description,
    packages=['went']
)
