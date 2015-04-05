import brainfuck
import unittest
from StringIO import StringIO


class HelloWorldTests(unittest.TestCase):
    def test_hello(self):
        with open("hello.bf") as f:
            self._test(f.read())

    def test_hello_small(self):
        with open("hellosmall.bf") as f:
            self._test(f.read())

    def _test(self, code):
        # Test function
        func = brainfuck.to_function(code)
        self.assertEqual(func(), "Hello World!\n")


if __name__ == "__main__":
    unittest.main()
