# -*- coding: utf-8 -*-
import unittest
from mongu import set_database, register_model, Model, enable_counter


class User(Model):
    _collection_ = 'users'
    _defaults_ = {'is_activated': False}

    def activate(self):
        self.is_activated = True


class NewUser(object):
    def __init__(self, save=False):
        self.save = save

    def __enter__(self):
        self.user = User(username='Mongu')
        if self.save:
            self.user.save()
        return self.user

    def __exit__(self, type, value, traceback):
        self.user.delete()


class TestCase(unittest.TestCase):
    def setUp(self):
        set_database('test')
        self.User = register_model(User)
        self.new_user = NewUser

    def tearDown(self):
        self.User.collection.drop()


class CounterTestCase(unittest.TestCase):
    def setUp(self):
        set_database('test')
        self.Counter, CounterMixin = enable_counter()

        class UserWithCounter(CounterMixin, User):
            _collection_ = 'user_with_counter'

        self.User = register_model(UserWithCounter)
        self.new_user = NewUser

    def tearDown(self):
        self.User.collection.drop()
        self.Counter.collection.drop()
