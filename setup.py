from setuptools import setup, find_packages

classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Software Development :: Compilers
Operating System :: Unix
"""

long_description = """\
JUGS (JavaScript UGlifier) is a JavaScript source-to-source compiler
and optimizer.
It compiles JavaScript into more compact code so that it downloads
and runs faster.
"""

setup(
    name='jugs',
    version='0.1',
    url='http://github.com/rspivak/jugs',
    license='MIT',
    description='JUGS - JavaScript Compiler / Optimizer',
    author='Ruslan Spivak',
    author_email='ruslan.spivak@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['setuptools'],
    zip_safe=False,
    entry_points="""\
    [console_scripts]
    jugs = jugs.compiler:main
    """,
    classifiers=filter(None, classifiers.split('\n')),
    long_description=long_description,
    extras_require={'test': []}
    )
