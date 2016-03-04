import sys
import brainfuck
import unittest
try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO


def _exec(module, globals_, locals_):
    exec(compile(module, "<brainfuck>", "exec"), globals_, locals_)


class ProgramTests(unittest.TestCase):
    def test_hello(self):
        self._test("programs/hello.bf", "", "Hello World!\n")

    def test_hello_small(self):
        self._test("programs/hellosmall.bf", "", "Hello World!\n")

    def test_rot13(self):
        self._test("programs/rot13.bf", "foobar", "sbbone")

    def _test(self, filename, input_str, expected_output):
        with open(filename, "r") as f:
            code = f.read()
        # Test function
        func = brainfuck.to_function(code)
        self.assertEqual(func(input_str), expected_output)
        # Test procedure
        func = brainfuck.to_procedure(code)
        out_, in_ = StringIO(), StringIO(input_str)
        func(out_, in_)
        self.assertEqual(out_.getvalue(), expected_output)
        # Test module
        module = brainfuck.to_module(code)
        out_, in_ = StringIO(), StringIO(input_str)
        old_out, old_in = sys.stdout, sys.stdin
        try:
            sys.stdout, sys.stdin = out_, in_
            _exec(module, globals(), locals())
        finally:
            sys.stdout, sys.stdin = old_out, old_in
        self.assertEqual(out_.getvalue(), expected_output)


class ImportHookTests(unittest.TestCase):
    def setUp(self):
        sys.path.append("programs")

    def tearDown(self):
        sys.path.remove("programs")
        brainfuck.remove_import_hook()
        # Remove imported brainfuck modules
        for key, module in list(sys.modules.items()):
            if hasattr(module, "__brainfuck_function__"):
                del sys.modules[key]

    def test_no_hook(self):
        with self.assertRaises(ImportError):
            import hello

    def test_install_hook(self):
        brainfuck.install_import_hook()
        import hello
        self.assertEqual(hello(), "Hello World!\n")

    def test_submodule(self):
        brainfuck.install_import_hook()
        import subdir.subhello
        self.assertEqual(subdir.subhello(), "Hello World!\n")

    def test_remove_hook(self):
        brainfuck.install_import_hook()
        brainfuck.remove_import_hook()
        with self.assertRaises(ImportError):
            import hello
        for importer in sys.meta_path:
            self.assertFalse(isinstance(importer, brainfuck.BrainfuckImporter))

    def test_custom_importer(self):
        cache = {"called": False}
        class Importer(brainfuck.BrainfuckImporter):
            def load_module(self, fullname):
                cache["called"] = True
                return super(Importer, self).load_module(fullname)

        brainfuck.install_import_hook(importer=Importer())
        import hello
        self.assertTrue(cache["called"])

    def test_custom_kwargs(self):
        brainfuck.install_import_hook(file_extensions=("bar",))
        for importer in sys.meta_path:
            if isinstance(importer, brainfuck.BrainfuckImporter):
                break
        self.assertEqual(importer.file_extensions, ("bar",))


if __name__ == "__main__":
    unittest.main()
