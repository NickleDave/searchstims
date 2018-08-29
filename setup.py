import os

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'visualsearchstim'
DESCRIPTION = 'Python package that generates images like the stimuli used in visual search experiments'
URL = 'https://github.com/NickleDave/make-vis-search-stim-pygame'
EMAIL = 'nicholdav at gmail dot com'
AUTHOR = 'David Nicholson'

# What packages are required for this module to be executed?
REQUIRED = [
    'pygame',
]

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name=NAME,
    #version=about['__version__'],
    description=DESCRIPTION,
    # long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    include_package_data=True,
    license='BSD-3',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],

)
