from setuptools import setup, find_packages

classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Software Development :: Compilers
Operating System :: Unix
"""

long_description = """\
SlimIt is a JavaScript source-to-source compiler and optimizer / minifier.
It compiles JavaScript into more compact code so that it downloads
and runs faster.
"""

setup(
    name='slimit',
    version='0.1dev',
    url='http://github.com/rspivak/slimit',
    license='MIT',
    description='SlimIt - JavaScript minifier',
    author='Ruslan Spivak',
    author_email='ruslan.spivak@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['distribute', 'ply'],
    zip_safe=False,
    entry_points="""\
    [console_scripts]
    """,
    classifiers=filter(None, classifiers.split('\n')),
    long_description=long_description,
    extras_require={'test': []}
    )
