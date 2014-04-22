# -*- coding: utf-8 -*-
from .base import TestCase
from mongu import Client
from pymongo import MongoClient


class ClientTests(TestCase):
    def test_default(self):
        self.assertEqual(Client().client, MongoClient())

    def test_uri(self):
        self.assertEqual(
            Client('mongodb://localhost:27017').client,
            MongoClient('mongodb://localhost:27017'))

    def test_warning(self):
        self.assert_warn(SyntaxWarning, Client, 'mongodb://localhost:27017/database')
