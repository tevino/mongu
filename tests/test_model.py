# -*- coding: utf-8 -*-
import unittest

from mongu import set_database, register_model, Model


class TestCase(unittest.TestCase):
    def setUp(self):
        set_database('test')

        @register_model
        class User(Model):
            _collection_ = 'users'
            _defaults_ = {
                'is_activated': False,
            }

            def activate(self):
                self.is_activated = True

        self.User = User

    def tearDown(self):
        self.User.collection.drop()


class BasicTestCase(TestCase):
    def test_basic(self):
        user = self.User(username='Mongu')

        assert not user.is_activated
        user.activate()
        assert user.is_activated

        assert '_id' not in user
        user.save()
        assert '_id' in user
        assert user.id == str(user._id)

        user == self.User.by_id(user.id)

        user.delete()

    def test_creation(self):
        for name in ('Mongu', 'Rocks'):
            self.User(username=name).save()

        self.assertEqual(len(list(self.User.find({'username': 'Rocks'}))), 1)


if __name__ == '__main__':
    unittest.main()
