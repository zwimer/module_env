import unittest

from module_env import ModuleEnv, InverseModuleEnv


class SingleEnv(unittest.TestCase):
    def setUp(self) -> None:
        self.env = ModuleEnv()
        self.inv: InverseModuleEnv = self.env.inverse()


class DualEnv(SingleEnv):
    def setUp(self) -> None:
        super().setUp()
        self.env2 = ModuleEnv()
        self.inv2: InverseModuleEnv = self.env2.inverse()
