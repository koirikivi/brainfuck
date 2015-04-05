import ast
import sys
from collections import defaultdict
from textwrap import dedent
from StringIO import StringIO


def to_function(code):
    """Parse brainfuck code to a function that takes a string as input
    parameter and returns a string"""
    procedure = to_procedure(code)
    def _brainfuck(input_str=""):
        output = StringIO()
        input = StringIO(input_str)
        procedure(output=output, input=input)
        return output.getvalue()
    return _brainfuck


def to_procedure(code):
    """Parse brainfuck code to a procedure that takes two file-like objects as
    parameters, the streams for output and input (if none are given,
    stdout/stdin are used)"""
    module = ast.Module(body=parse_ast(code))
    module = ast.fix_missing_locations(module)
    def _brainfuck(output=None, input=None):
        if output is None:
            output = sys.stdout
        if input is None:
            input = sys.stdin
        data_ptr = 0
        memory = defaultdict(int)
        exec compile(module, "<brainfuck>", "exec") in globals(), locals()
    return _brainfuck


def to_module(code):
    """Parse brainfuck code to an AST module that can be executed"""
    module = ast.parse(dedent("""\
    from sys import stdout as output, stdin as input
    from collections import defaultdict
    data_ptr = 0
    memory = defaultdict(int)
    """))
    instructions = parse_ast(code)
    module,body.extend(instructions)
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
            instructions.append(_parse_node(
                "memory[data_ptr] = ord(input.read(1))"))
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


if __name__ == "__main__":
    with open("hello.bf", "r") as f:
        hello_code = f.read()
    hello_procedure = to_procedure(hello_code)
    hello_procedure()
    hello_function = to_function(hello_code)
    print hello_function()
