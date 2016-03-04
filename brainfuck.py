"""
brainfuck.py - brainfuck-to-python-AST compiler and related utilities

This module provides utilities for seamless usage of brainfuck programs in
Python environments. The meat of the module consists of the `to_*` functions
that convert code written in brainfuck to native Python datatypes, such as
functions or modules. The conversion is done using the Python abstract syntax
tree (AST), which enables flexible, run-time integration between the two
languages.

An import hook is also provided for convenience. It can be installed by calling
`install_import_hook`, after which brainfuck modules (with the file extennsion
as "bf" or "b" by default) can be imported anywhere from sys.path.

License: MIT
"""
import ast
import os
import sys
import types
from textwrap import dedent


__version__ = "0.9.1"
__all__ = ("to_function", "to_procedure", "to_module", "parse_ast",
           "BrainfuckImporter", "install_import_hook", "remove_import_hook")


def to_function(code):
    """Parse brainfuck code to a function that takes a string as an input
    parameter and returns a string"""

    module = ast.parse(dedent("""\
    def _brainfuck(input_str=""):
        try:
            from cStringIO import StringIO
        except ImportError:
            try:
                from StringIO import StringIO
            except ImportError:
                from io import StringIO
        from collections import defaultdict
        data_ptr = 0
        memory = defaultdict(int)
        output = StringIO()
        input = StringIO(input_str)
    """))
    return_statement = _parse_node("return output.getvalue()")
    brainfuck_instructions = parse_ast(code)
    function = module.body[0]
    function.body.extend(brainfuck_instructions)
    function.body.append(return_statement)
    module = ast.fix_missing_locations(module)
    exec(compile(module, "<brainfuck>", "exec"), globals(), locals())
    return locals()["_brainfuck"]


def to_procedure(code):
    """Parse brainfuck code to a procedure that takes two file-like objects as
    parameters, the streams for output and input (if none are given,
    stdout/stdin are used)"""
    module = ast.parse(dedent("""\
    def _brainfuck(output=None, input=None):
        import sys
        from collections import defaultdict
        data_ptr = 0
        memory = defaultdict(int)
        if output is None:
            output = sys.stdout
        if input is None:
            input = sys.stdin
    """))
    brainfuck_instructions = parse_ast(code)
    function = module.body[0]
    function.body.extend(brainfuck_instructions)
    module = ast.fix_missing_locations(module)
    exec(compile(module, "<brainfuck>", "exec"), globals(), locals())
    return locals()["_brainfuck"]


def to_module(code):
    """Parse brainfuck code to an AST module that can be executed"""
    module = ast.parse(dedent("""\
    from sys import stdout as output, stdin as input
    from collections import defaultdict
    data_ptr = 0
    memory = defaultdict(int)
    """))
    instructions = parse_ast(code)
    module.body.extend(instructions)
    module = ast.fix_missing_locations(module)
    return module


def parse_ast(code):
    """
    Return a list of of AST instructions from code given as a string

    The instructions can be used as a body of another AST node (e.g. a module).
    The following variables need to be present in the scope where the
    instructions are executed:

    - `data_ptr`: integer, initialized to 0
    - `memory`: array of infinite length, every cell initialized to 0
      (can be implemented using `defaultdict(int)`
    - `output`: file-like object for character output
    - `input`: file-like object for character input
    """
    instructions = []
    instruction_stack = []
    for char in code:
        # Note: some cycles could be saved by inlining these instead of parsing
        # from strings. However, who cares.
        if char == ">":
            instructions.append(_parse_node(
                "data_ptr += 1"))
        elif char == "<":
            instructions.append(_parse_node(
                "data_ptr -= 1"))
        elif char == "+":
            instructions.append(_parse_node(
                "memory[data_ptr] += 1"))
        elif char == "-":
            instructions.append(_parse_node(
                "memory[data_ptr] -= 1"))
        elif char == ".":
            instructions.append(_parse_node(
                "output.write(chr(memory[data_ptr]))"))
        elif char == ",":
            # NOTE: EOF behaviour is not well defined in brainfuck
            # in this implementation, -1 is used
            instructions.append(_parse_node(
                "_tmp = input.read(1)"))
            instructions.append(_parse_node(
                "memory[data_ptr] = ord(_tmp) if _tmp else -1"))
        elif char == "[":
            node = _parse_node("while memory[data_ptr]: pass")
            instructions.append(node)
            instruction_stack.insert(0, instructions)
            instructions = node.body
        elif char == "]":
            # TODO: catch parse error
            instructions = instruction_stack.pop(0)

    return instructions


def _parse_node(expression):
    module = ast.parse(expression)
    assert len(module.body) == 1
    return module.body[0]


class BrainfuckModule(types.ModuleType):
    def __init__(self, fullname, code):
        super(BrainfuckModule, self).__init__(fullname)
        self.__brainfuck_code__ = code
        self.__brainfuck_function__ = to_function(code)
        _, _, func_name = fullname.rpartition(".")
        setattr(self, func_name, self.__brainfuck_function__)

    def __call__(self, input_str=""):
        return self.__brainfuck_function__(input_str)


class BrainfuckImporter(object):
    """Import hook that finds brainfuck files anywhere in the system path and
    loads them as modules"""

    def __init__(self, file_extensions=("bf", "b"),
                 module_type=BrainfuckModule):
        self.file_extensions = file_extensions
        self.module_type = module_type

    def find_module(self, fullname, path=None):
        if self._find_module_path(fullname):
            return self
        return None

    def load_module(self, fullname):
        if fullname in sys.modules:
            # Cached
            return sys.modules[fullname]

        path = self._find_module_path(fullname)
        if not path:
            raise ImportError
        with open(path, "r") as f:
            code = f.read()

        module = self.module_type(fullname, code)
        module.__loader__ = self

        sys.modules[fullname] = module

        return module

    def _find_module_path(self, fullname):
        parts = fullname.split(".")
        for base_path in sys.path:
            for extension in self.file_extensions:
                filename = "{}.{}".format(parts[-1], extension)

                path_parts = []
                if base_path:
                    path_parts.append(base_path)
                path_parts.extend(parts[:-1])
                path_parts.append(filename)

                full_path = os.path.join(*path_parts)
                if os.path.exists(full_path):
                    return full_path
        return None


def install_import_hook(importer=None, **kwargs):
    """Install a module importer that finds and loads brainfuck files

    Replace existing loader if one exists (and return False), return True if no
    existing loader was found.

    The importer can be speficied as a parameter, as can keyword arguments that
    are passed to it. In this case, the importer is assumed to be derived from
    the BrainfuckImporter class.
    """
    if importer is None:
        importer = BrainfuckImporter(**kwargs)

    for i, current in enumerate(sys.meta_path):
        if isinstance(current, BrainfuckImporter):
            sys.meta_path[i] = importer
            return False
    sys.meta_path.append(importer)
    return True


def remove_import_hook():
    """Remove the brainfuck module importer from system module importers"""
    # NOTE: removing the import hook still leaves all imported brainfuck
    # modules in sys.modules
    for i, importer in enumerate(sys.meta_path):
        if isinstance(importer, BrainfuckImporter):
            del sys.meta_path[i]
            return True
    return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: {} <brainfuck file>".format(sys.argv[0]))
        sys.exit(1)
    with open(sys.argv[1], "r") as f:
        code = f.read()
    to_procedure(code)()
