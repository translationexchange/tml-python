"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
from __future__ import absolute_import

import os
import sys
import re
# Always prefer setuptools over distutils
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages
# To use a consistent encoding
from codecs import open
pj = os.path.join
dirname = os.path.dirname
abspath = os.path.abspath

# need to kill off link if we're in docker builds
if os.environ.get('PYTHON_BUILD_DOCKER', None) == 'true':
    del os.link

def get_version(*path):
    filename = pj(dirname(__file__), *path)
    version_file = open(filename, encoding='utf-8').read()
    version_match = re.search(r"^__VERSION__ = (['\"])([^'\"]*)\1",
                              version_file, re.M)
    if version_match:
        groups = version_match.groups()
        if len(groups) > 1:
            return version_match.group(2)
    raise RuntimeError('Unable to find version string.')

version = get_version('tml', '__init__.py')
here = abspath(dirname(__file__))

# Get the long description from the relevant file



if sys.argv[-1] == 'publish':
    try:
        import wheel
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -f -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags --force")
    sys.exit()


with open(pj(here, 'README.md'), encoding='utf-8') as f:
    readme = f.read()
with open(pj(here, 'HISTORY.rst'), encoding='utf-8') as f:
    history = f.read()

requirements = [
    'requests==2.7.0',
    'six==1.10.0',
    'lxml==3.6.0'
]


setup(
    name='tml',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,

    description='Python SDK for tranlationexchange.com',
    long_description=readme,
    # The project's main homepage.
    url='https://github.com/translationexchange/tml-python.git',
    # Author details
    author='Translation Exchange, Inc.',
    author_email='r.kamun@gmail.com',
    # Choose your license
    license='MIT',
    zip_safe=False,
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='tml tml-python translationexchange',
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=requirements,
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[memcached,pylibmc] or
    # tml django setup.py: install_requires = ["tml[memcached]"],
    extras_require={
        'memcached': ['python-memcached>=1.57'],
        'pylibmc': ['pylibmc>=1.5.0'],
        'redis': ['redis==2.10.5']
    },

)
