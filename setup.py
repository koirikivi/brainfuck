from setuptools import setup
from codecs import open
from os import path
import brainfuck


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


classifiers = [
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Compilers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
]


setup(
    name='python-brainfuck',
    version=brainfuck.__version__,
    description='Brainfuck to Python AST compilation and integration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/koirikivi/brainfuck',
    author='Rainer Koirikivi',
    author_email='rainer@koirikivi.fi',
    license='MIT',
    keywords='python brainfuck ast compiler integration',
    py_modules=['brainfuck'],
    classifiers=classifiers, 
)
