# -*- coding: utf-8 -*-
import time
import warnings
import unittest
from mongu import Client, Model


class User(Model):
    _database_ = 'test'
    _collection_ = 'users'
    _defaults_ = {
        'is_activated': False,
        'created_at': time.time
    }

    def activate(self):
        self.is_activated = True


class Admin(User):
    _defaults_ = {'role': 'admin'}


def new_user(model):
    class NewUser(object):
        def __init__(self, save=False):
            self.save = save

        def __enter__(self):
            self.user = model(username='Mongu')
            if self.save:
                self.user.save()
            return self.user

        def __exit__(self, type, value, traceback):
            self.user.delete()
    return NewUser


class TestCase(unittest.TestCase):
    def assert_warn(self, warn, func, *args, **kwargs):
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            # warnings.simplefilter("always")
            res = func(*args, **kwargs)
            assert issubclass(w[-1].category, warn)
        return res

    def setUp(self):
        c = Client()
        self.User = c.register_model(User)
        self.new_user = new_user(User)
        self.new_admin = new_user(Admin)

    def tearDown(self):
        self.User.collection.drop()


class CounterBase(object):
    @classmethod
    def increase_by_6(self, key):
        return self.change_by(key, 6)


class CounterTestCase(unittest.TestCase):
    def setUp(self):
        c = Client()
        self.Counter, CounterMixin = c.enable_counter(base=CounterBase)

        class UserWithCounter(CounterMixin, User):
            _collection_ = 'user_with_counter'

        self.User = c.register_model(UserWithCounter)
        self.new_user = new_user(User)

    def tearDown(self):
        self.User.collection.drop()
        self.Counter.collection.drop()
