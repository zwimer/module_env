import unittest
import sys

from module_env import ModuleEnv, InverseModuleEnv

from common import SingleEnv


class TestInit(unittest.TestCase):
    def test_constructible(self):
        _ = ModuleEnv()

    def test_default(self):
        self.assertNotEqual(len(ModuleEnv()._sys.obj._attrs), 0)

    def test_configurable(self):
        self.assertEqual(len(ModuleEnv(sys_attrs=tuple())._sys.obj._attrs), 0)

    def test_inverse(self):
        self.assertIsInstance(ModuleEnv().inverse(), InverseModuleEnv)


class TestFundamentals(SingleEnv):
    def test_inverse_inverse(self):
        self.assertIsInstance(self.inv.inverse(), ModuleEnv)

    def test_context_manager(self):
        with self.env as env:
            self.assertIs(self.env, env)
            with self.inv as inv:
                self.assertIs(self.inv, inv)

    def test_get(self):
        with self.env:
            self.assertIs(sys.modules["unittest"], unittest)
            self.assertIs(self.env["unittest"], unittest)
        with self.env, self.inv:
            self.assertIs(sys.modules["unittest"], unittest)
            self.assertIs(self.inv["unittest"], unittest)


if __name__ == "__main__":
    unittest.main()
