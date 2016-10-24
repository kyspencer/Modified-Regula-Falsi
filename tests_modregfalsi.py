# tests_modregfalsi.py
#   Author: Kristy Yancey Spencer
#
#   This script performs unit testing for modregulafalsi.py

import unittest
from modregulafalsi import MyClass


class ModRegFalsiTests(unittest.TestCase):

    def setUp(self):
        self.example = MyClass()

    def test_modregulafalsi(self):
        ck = self.example.modregulafalsi(0.0, 1.0)
        self.assertTrue(0.69 < ck < 0.70)

    def test_findnewinput(self):
        # Check if module returns old t0 and t1
        self.assertEqual(self.example.findnewinput(0.0, 1.0), (0.0, 1.0))
        # Check if module returns new t0 and t1
        x0, x1 = self.example.findnewinput(0.0, 0.5)
        self.assertEqual(x0, 0.5)
        self.assertGreater(x1, 0.69)

    def test_function(self):
        y = self.example.function(0)
        self.assertEqual(y, -1)

    def test_newx_regfalsi(self):
        ck = self.example.newx_regfalsi(0.0, 1.0)
        self.assertEqual(ck, 0.5)

    def test_newx_modregfalsi(self):
        ck = self.example.newx_modregfalsi(0.0, 1.0, 1, 0.5)
        self.assertEqual(ck, 2.0/3.0)


if __name__ == '__main__':
    unittest.main()
