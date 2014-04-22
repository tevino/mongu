# -*- coding: utf-8 -*-
from bson import ObjectId
from bson.errors import InvalidId
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

    def test_find(self):
        s = 'i need a lot of users!'
        for name in s:
            self.User(name=name).save()
        self.assertEqual(len(list(self.User.find({'name': 'nobody'}))), 0)
        count = 0
        for user in self.User.find({'name': 'e'}):
            assert isinstance(user, self.User)
            count += 1
        self.assertEqual(count, s.count('e'))

        # test find_one
        nobody = self.User.find_one({'name': 'nobody'})
        self.assertEqual(nobody, None)
        somebody = self.User.find_one({'name': '!'})
        assert isinstance(somebody, self.User)

    def test_save(self):
        with self.new_user() as u:
            assert '_id' not in u
            u.save()
            assert '_id' in u

    def test_id(self):
        with self.new_user(save=True) as u:
            assert u.id == str(u._id)

            assert u == self.User.by_id(u.id)
        self.assertEqual(self.User.by_id(''), None)
        self.assertRaises(InvalidId, self.User.by_id, 'blabla')
        self.assertEqual(self.User.by_id(ObjectId()), None)

    def test_reload(self):
        with self.new_user(save=True) as u:
            u.collection.find_and_modify(
                {'username': u.username},
                {'$set': {'is_activated': False}})
            u.reload()
            assert not u.is_activated
            u.reload({'is_activated': True})
            assert u.is_activated
            assert 'username' not in u

    def test_delete(self):
        with self.new_user(save=True) as u:
            assert u.collection.find_one({'_id': u._id})
            u.delete()
            assert not u.collection.find_one({'_id': u._id})

    def test_creation(self):
        for name in ('Mongu', 'Rocks'):
            self.User(username=name).save()

        self.assertEqual(len(list(self.User.find({'username': 'Rocks'}))), 1)

    # Deprecated
    def test_from_dict(self):
        self.assertEqual(self.User.from_dict(None).keys(), self.User().keys())
