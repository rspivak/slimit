import os, sys

from setuptools import setup, find_packages
try:
   from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
   from distutils.command.build_py import build_py


classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Software Development :: Compilers
Operating System :: Unix
"""

requirements = ['ply>=3.4']
major, minor = sys.version_info[:2] # Python version
if major == 2 and minor <=6:
    # OrderedDict was added to the collections module in Python 2.7 and it is
    # there in all versions of Python 3.
    requirements.append('odict')
if major == 3:
    PYTHON3 = True
    try:
        import lib2to3 # Just a check--the module is not actually used
    except ImportError:
        print("Python 3.X support requires the 2to3 tool.")
        sys.exit(1)

def read(*rel_names):
    return open(os.path.join(os.path.dirname(__file__), *rel_names)).read()


setup(
    name='slimit',
    version='0.8.1',
    url='http://slimit.readthedocs.org',
    cmdclass = {'build_py': build_py},
    license='MIT',
    description='SlimIt - JavaScript minifier',
    author='Ruslan Spivak',
    author_email='ruslan.spivak@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    zip_safe=False,
    entry_points="""\
    [console_scripts]
    slimit = slimit.minifier:main
    """,
    classifiers=filter(None, classifiers.split('\n')),
    long_description=read('README.rst') + '\n\n' + read('CHANGES'),
    extras_require={'test': []}
    )

