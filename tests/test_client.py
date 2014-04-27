# -*- coding: utf-8 -*-
from .base import TestCase
from mongu import Client, Model, ModelAttributeError
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

    def test_no_database(self):
        class BrokenModel(Model):
            _collection_ = 'test'
        self.assertRaises(ModelAttributeError, self.client.register_model, BrokenModel)

    def test_no_collection(self):
        class BrokenModel(Model):
            _database_ = 'test'
        self.assertRaises(ModelAttributeError, self.client.register_model, BrokenModel)

    def test_no_registration(self):
        class MyModel(Model):
            _database_ = 'test'
            _collection_ = 'test'
        self.assertRaises(ModelAttributeError, getattr, MyModel, 'collection')
