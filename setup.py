import os

from setuptools import setup, find_packages


classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Software Development :: Compilers
Operating System :: Unix
"""

def read(*rel_names):
    return open(os.path.join(os.path.dirname(__file__), *rel_names)).read()


setup(
    name='slimit',
    version='0.6',
    url='http://slimit.org',
    license='MIT',
    description='SlimIt - JavaScript minifier',
    author='Ruslan Spivak',
    author_email='ruslan.spivak@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['distribute', 'ply>=3.4', 'odict'],
    zip_safe=False,
    entry_points="""\
    [console_scripts]
    slimit = slimit.minifier:main
    """,
    classifiers=filter(None, classifiers.split('\n')),
    long_description=read('README.rst') + '\n\n' + read('CHANGES'),
    extras_require={'test': []}
    )
