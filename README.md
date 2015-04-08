brainfuck.py - seamless usage of Brainfuck in Python code
=========================================================

brainfuck.py compiles Brainfuck programs to Python AST, enabling the
integration of industial-strength Brainfuck programs with Python code. Example:

```python
>>> import brainfuck
>>> hello = brainfuck.to_function("""
    ++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>
    .>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.
    """)
>>> hello()
'Hello World!\n'
```

For convenience, an import hook is also provided:

```python
>>> brainfuck.install_import_hook()
>>> # Note: programs is a python package (with __init__.py
    # and a brainfuck file named rot13.bf)
>>> from programs import rot13  
>>> rot13.rot13("brainfuck")
'oenvashpx'
>>> # The module can also be called directly
>>> rot13("foobar")
'sbbone'
```


Installation
------------

```
$ pip install brainfuck
```

OR

```
$ git clone git@github.com:koirikivi/brainfuck.git
$ cd brainfuck
$ python setup.py install
```

OR just copy ``brainfuck.py`` somewhere in your PYTHONPATH.


Platform support
----------------

Latest versions of Python 2, 3 and PyPy are supported and tested. Other Python
versions that have support for the ``ast`` module should work too, but are not
tested.


Unit tests
----------

Run tests with ``$ python test_brainfuck.py``


TODO
----

- Optimizations for the brainfuck-generated AST  (this is a big one!)
- More tests
- Running tests with tox
- Python AST to brainfuck compilation (may take some time)


License
-------

MIT (programs in the programs-directory may be licensed differently)
