from __future__ import print_function
import timeit

setup = """\
import brainfuck
with open("programs/hello.bf", "r") as f:
    code = f.read()
hello = brainfuck.to_function(code)
with open("programs/rot13.bf", "r") as f:
    code = f.read()
rot13 = brainfuck.to_function(code)
"""

stmt = r"""\
result = hello()
assert result == "Hello World!\n"
result = rot13("foobar")
assert result == "sbbone"
"""

print("Time taken: ", end="")
print(timeit.timeit(stmt=stmt, setup=setup, number=1000))
