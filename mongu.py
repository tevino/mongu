# -*- coding: utf-8 -*-

__version__ = '0.2.1'

import logging
from bson import ObjectId
from pymongo import MongoClient


def register_model(model_cls):
    """Decorator for registering model."""
    if not getattr(model_cls, '_database_'):
        raise Exception('Database not set on %s!' % model_cls.__name__)
    if not getattr(model_cls, '_collection_'):
        raise Exception('Collection not set on %s!' % model_cls.__name__)

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


class class_property(object):
    """Calls the decorator method on class attribute access."""
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class Model(ObjectDict):
    """Dict-like class with optional default key-values
    that binds to a collection."""
    _database_ = None
    _collection_ = None
    _defaults_ = {}

    @class_property
    def collection(self):
        return getattr(MongoClient()[self._database_], self._collection_)

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        for k, v in self._defaults_.iteritems():
            value = v() if callable(v) else v
            self.setdefault(k, value)

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
    @classmethod
    def change_by(cls, name, num):
        """Change counter of ``name`` by ``num`` (can be negative)."""
        count = cls.count(name)
        if count + num < 0:
            raise Exception(u'Counter[%s] must be bigger than 0 after %+d.' % (name, num))

        counter = cls.collection.find_and_modify(
            {'name': name},
            {'$inc': {'seq': num}},
            new=True,
            upsert=True
        )
        return counter['seq']

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


def enable_counter(base=None, database='counter', collection='counters'):
    """Register the builtin counter model, return the registered Counter class
    and the corresponding ``CounterMixin`` class.

    It automatically increases or decreases the counter of model class after model
    creation(save without ``_id``) and deletion.

    There is a classmethod ``count()`` added to the model class that returns the current
    count of model collection."""
    Counter._database_ = database
    Counter._collection_ = collection
    bases = (base, Counter) if base else (Counter,)
    counter = register_model(type('Counter', bases, {}))

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
