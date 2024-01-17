import unittest

from module_env import ModuleEnv


class SingleEnv(unittest.TestCase):
    def setUp(self) -> None:
        self.env = ModuleEnv()
        self.inv = self.env.inverse()


class DualEnv(SingleEnv):
    def setUp(self) -> None:
        super().setUp()
        self.env2 = ModuleEnv()
        self.inv2 = self.env2.inverse()
