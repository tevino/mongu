# -*- coding: utf-8 -*-
from .test_model import ModelTests
from .test_counter import CounterTests


def suite():
    import unittest
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for case in (ModelTests, CounterTests):
        suite.addTests(loader.loadTestsFromTestCase(case))
    return suite
