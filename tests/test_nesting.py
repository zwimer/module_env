import unittest

from module_env import UsageError

from common import DualEnv


class TestInvalidNesting(DualEnv):
    def test_env_in_env(self):
        with self.env, self.assertRaises(UsageError), self.env:
            pass

    def test_env2_in_env(self):
        with self.env, self.assertRaises(UsageError), self.env2:
            pass

    def test_inv2_in_inv(self):
        with self.env, self.inv, self.assertRaises(UsageError), self.inv2:
            pass


class TestValidNesting(DualEnv):
    def test_env_depth_1(self):
        with self.env, self.inv, self.env:
            pass

    def test_env_depth_2(self):
        with self.env, self.inv:
            self.test_env_depth_1()

    def test_env2_in_inv_in_env(self):
        with self.env, self.inv, self.env:
            pass


if __name__ == "__main__":
    unittest.main()
