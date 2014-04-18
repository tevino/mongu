# -*- coding: utf-8 -*-
"""
**Mongu** is yet another Python Object-Document Mapper on top of ``PyMongo``. It's lightweight, intuitive to use and easy to understand.

- If you want **control**.
- If you really care about **performance**.
- If those **heavy and slow layers** have nothing or more than you need.

Well, **Mongu** maybe the one for you.

You are the only one who knows what you reall need.

Therefor **Mongu** does nothing but a skeleton for you to fill.

Actually, if you have ever tried to write your own ODM, you may already implemented parts of **Mongu** :D

Copyright (c) 2014, Tevin Zhang.
License: MIT (see LICENSE for details)
"""

__author__ = 'Tevin Zhang'
__version__ = '0.1'
__license__ = 'MIT'


import logging
from bson import ObjectId
from pymongo import MongoClient

DB_NAME = None


def set_database(db_name):
    """Invoke this before any model registration."""
    logging.info('Setting database to %s' % db_name)
    globals()['DB_NAME'] = db_name


def get_connection():
    """Return a MongoClient instance associated to database
    set by ``set_database``."""
    if not DB_NAME:
        raise Exception('Database must be set first!')
    return MongoClient()[DB_NAME]


def register_model(model_cls):
    """Decorator for registering model."""
    # set collection property
    model_cls.collection = getattr(get_connection(), model_cls._collection_)

    # merge _defaults_ from base classes
    defaults = {}
    for b_cls in model_cls.__bases__:
        defaults.update(getattr(b_cls, '_defaults_', {}))

    defaults.update(getattr(model_cls, '_defaults_', {}))
    model_cls._defaults_ = defaults

    logging.info('Registering Model ' + model_cls.__name__)
    return model_cls


class ObjectDict(dict):
    """Makes a dictionary behave like an object, with
    attribute-style access."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


class Model(ObjectDict):
    """Dict-like class with optional default key-values
    that binds to a collection."""
    _collection_ = None
    _defaults_ = {}

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        for k, v in self._defaults_.iteritems():
            self.setdefault(k, v)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, super(Model, self).__repr__())

    @classmethod
    def by_id(cls, oid):
        """Find a model object by its ``ObjectId``,
        ``oid`` can be string or ObjectId"""
        if oid:
            return cls.from_dict(cls.collection.find_one(ObjectId(oid)))

    @classmethod
    def from_dict(cls, d):
        """Build model object from a dict."""
        d = d or {}
        return cls(**d)

    @classmethod
    def from_cursor(cls, cursor):
        """Build model object from a pymongo cursor."""
        for d in cursor:
            yield cls.from_dict(d)

    @classmethod
    def find(cls, *args, **kwargs):
        """Same as ``collection.find``, return model object instead of simple dict."""
        return cls.from_cursor(cls.collection.find(*args, **kwargs))

    @classmethod
    def find_one(cls, *args, **kwargs):
        """Same as ``collection.find_one``, return model object instead of simple dict."""
        return cls.from_dict(
            cls.collection.find_one(*args, **kwargs))

    @property
    def id(self):
        """String representation of attribute ``_id``."""
        if '_id' in self:
            return str(self._id)

    def reload(self, d=None):
        """Reload model from given dict or database."""
        if d:
            self.clear()
            self.update(self.from_dict(d))
        elif self.id:
            new_dict = self.by_id(self._id)
            self.clear()
            self.update(new_dict)
        else:
            raise Exception('Model must be saved first.')

    def on_save(self, old_dict):
        """Hook after save."""
        pass

    def save(self):
        """Save model object to database."""
        d = dict(self)
        for k, v in self._defaults_.iteritems():
            if k not in d:
                v = v() if callable(v) else v
                d[k] = v
        old_dict = d.copy()
        _id = self.collection.save(d)
        self._id = _id
        self.on_save(old_dict)
        return self._id

    def on_delete(self, deleted_obj):
        """Hook after delete."""
        pass

    def delete(self):
        """Remove from database."""
        if self.id:
            self.collection.remove({'_id': self._id})
        self.on_delete(self)


class Counter(Model):
    """Builtin counter model."""
    _collection_ = None

    @classmethod
    def change_by(cls, name, num):
        """Change counter of ``name`` by ``num`` (can be negative)."""
        counter = cls.collection.find_and_modify(
            {'name': name},
            {'$inc': {'seq': num}},
            new=True,
            upsert=True
        )
        seq = counter['seq']
        if seq < 0:
            raise Exception(u'seq of %s should not be %s' % (name, seq))
        return seq

    @classmethod
    def increase(cls, name):
        """Increase counter of ``name`` by one."""
        return cls.change_by(name, 1)

    @classmethod
    def decrease(cls, name):
        """Decrease counter of ``name`` by one."""
        return cls.change_by(name, -1)

    @classmethod
    def count(cls, name):
        """Return the count of ``name``"""
        counter = cls.collection.find_one({'name': name}) or {}
        return counter.get('seq', 0)


def enable_counter(collection='counters', base=Model):
    """Register the builtin counter model, return the registered Counter class
    and the corresponding ``CounterMixin`` class.

    It automatically increases or decreases the counter of model class after model
    creation(save without ``_id``) and deletion.

    There is a classmethod ``count()`` added to the model class that returns the current
    count of model collection."""
    Counter._collection_ = collection
    counter = register_model(Counter)

    class CounterMixin(object):
        """Mixin class for model"""
        def on_save(self, old_dict):
            super(CounterMixin, self).on_save(old_dict)
            if not old_dict.get('_id'):
                counter.increase(self._collection_)

        def on_delete(self, *args, **kwargs):
            super(CounterMixin, self).on_delete(*args, **kwargs)
            counter.decrease(self._collection_)

        @classmethod
        def count(cls):
            return counter.count(cls._collection_)

    logging.info('Counter enabled on collection: %s' % collection)
    return counter, CounterMixin
