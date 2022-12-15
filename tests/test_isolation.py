import unittest
import sys

from common import SingleEnv


class TestIsolation(SingleEnv):
    mod: str = "dummy"

    def setUp(self) -> None:
        assert self.mod not in sys.modules
        self.new_path: str = "/abc"
        while self.new_path in sys.path:
            self.new_path += "-abc"
        super().setUp()

    def tearDown(self) -> None:
        while self.new_path in sys.path:
            sys.path.remove(self.new_path)
        globals().pop(self.mod, None)
        sys.modules.pop(self.mod, None)

    def test_env_import_module(self):
        with self.env:
            _ = __import__(self.mod)
            self.assertIn(self.mod, sys.modules)
        self.assertNotIn(self.mod, sys.modules)
        with self.env:
            self.assertIn(self.mod, sys.modules)

    def test_global_import_module(self):
        _ = __import__(self.mod)
        self.assertIn(self.mod, sys.modules)
        with self.env:
            self.assertNotIn(self.mod, sys.modules)
        self.assertIn(self.mod, sys.modules)

    def test_env_sys_persist(self):
        self.assertNotIn(self.new_path, sys.path)
        with self.env:
            sys.path.append(self.new_path)
            self.assertEqual(self.new_path, sys.path[-1])
        self.assertNotIn(self.new_path, sys.path)
        with self.env:
            self.assertEqual(self.new_path, sys.path[-1])

    def test_global_sys_persist(self):
        sys.path.append(self.new_path)
        self.assertEqual(self.new_path, sys.path[-1])
        with self.env:
            self.assertNotIn(self.new_path, sys.path)
        self.assertEqual(self.new_path, sys.path[-1])

    def test_inverse(self):
        _ = __import__(self.mod)
        self.assertIn(self.mod, sys.modules)
        with self.env:
            self.assertNotIn(self.mod, sys.modules)
            with self.inv:
                self.assertIn(self.mod, sys.modules)

    def test_getitem_env_import(self):
        with self.env:
            _ = self.env[self.mod]
            self.assertIn(self.mod, sys.modules)
        self.assertNotIn(self.mod, sys.modules)
        with self.env:
            self.assertIn(self.mod, sys.modules)

    def test_getitem_inverse_import(self):
        with self.env:
            with self.inv:
                _ = self.inv[self.mod]
                self.assertIn(self.mod, sys.modules)
            self.assertNotIn(self.mod, sys.modules)
        self.assertIn(self.mod, sys.modules)


if __name__ == "__main__":
    unittest.main()
