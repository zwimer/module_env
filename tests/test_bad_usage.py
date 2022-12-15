import unittest

from module_env import InverseModuleEnv, UsageError

from common import DualEnv


class TestBadUsageError(DualEnv):
    def test_child_outside_parent(self):
        with self.assertRaises(UsageError):
            with self.inv.inverse():
                pass

    def test_wrong_inversion(self):
        with self.env:
            with self.assertRaises(UsageError):
                with self.inv2:
                    pass

    def test_inverses_are_siblings_not_same(self):
        with self.env:
            with self.inv:
                inv_inv = self.env.inverse().inverse()
                self.assertIsNot(inv_inv, self.inv.inverse())
                with self.assertRaises(UsageError):
                    with inv_inv:
                        pass

    def test_inv_direct(self):
        with self.assertRaises(UsageError):
            with self.inv:
                pass

    def test_private_ctor(self):
        with self.assertRaises(UsageError):
            _ = InverseModuleEnv()

    def test_get_direct(self):
        with self.assertRaises(UsageError):
            self.env["unittest"]
        with self.assertRaises(UsageError):
            self.inv["unittest"]

    def test_get_in_wrong_env(self):
        with self.env:
            with self.assertRaises(UsageError):
                self.env2["unittest"]
        with self.env:
            with self.assertRaises(UsageError):
                self.inv["unittest"]

    def test_inv2_get_in_inv(self):
        with self.env:
            with self.inv:
                with self.assertRaises(UsageError):
                    self.inv2["unittest"]


if __name__ == "__main__":
    unittest.main()
