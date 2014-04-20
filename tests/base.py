# -*- coding: utf-8 -*-
import time
import unittest
from mongu import set_database, register_model, Model, enable_counter


class User(Model):
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
    def setUp(self):
        set_database('test')
        self.User = register_model(User)
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
        set_database('test')
        self.Counter, CounterMixin = enable_counter(base=CounterBase)

        class UserWithCounter(CounterMixin, User):
            _collection_ = 'user_with_counter'

        self.User = register_model(UserWithCounter)
        self.new_user = new_user(User)

    def tearDown(self):
        self.User.collection.drop()
        self.Counter.collection.drop()
