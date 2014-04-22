# -*- coding: utf-8 -*-
from .test_model import ModelTests
from .test_counter import CounterTests
from .test_client import ClientTests


def suite():
    import unittest
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for case in (ClientTests, ModelTests, CounterTests):
        suite.addTests(loader.loadTestsFromTestCase(case))
    return suite
