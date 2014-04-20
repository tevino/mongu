# -*- coding: utf-8 -*-
from .base import TestCase


class ModelTests(TestCase):
    def test_defaults(self):
        with self.new_user() as u:
            assert not u.is_activated
            assert isinstance(u.created_at, float)

    def test_defaults_inheritance(self):
        with self.new_admin() as a:
            self.assertEqual(a.role, 'admin')
            a.activate()
            assert a.is_activated

    def test_method(self):
        with self.new_user() as u:
            u.activate()
            assert u.is_activated

    def test_save(self):
        with self.new_user() as u:
            assert '_id' not in u
            u.save()
            assert '_id' in u

    def test_id(self):
        with self.new_user(save=True) as u:
            assert u.id == str(u._id)

            u == self.User.by_id(u.id)

    def test_reload(self):
        with self.new_user(save=True) as u:
            u.collection.find_and_modify(
                {'username': u.username},
                {'$set': {'is_activated': False}})
            u.reload()
            assert not u.is_activated

    def test_delete(self):
        with self.new_user(save=True) as u:
            assert u.collection.find_one({'_id': u._id})
            u.delete()
            assert not u.collection.find_one({'_id': u._id})

    def test_creation(self):
        for name in ('Mongu', 'Rocks'):
            self.User(username=name).save()

        self.assertEqual(len(list(self.User.find({'username': 'Rocks'}))), 1)
