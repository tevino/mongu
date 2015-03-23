# -*- coding: utf-8 -*-

__version__ = '0.4.4'

import logging
import warnings
from collections import Callable
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import ConfigurationError


class Client(object):
    """For Connecting to MongoDB and registering model classes."""
    def __init__(self, *args, **kwargs):
        """Accept arguments same as ``MongoClient``.

        example::

            >> Client('localhost', 27017)
            >> Client('mongodb://localhost:27017')
        """
        self.client = MongoClient(*args, **kwargs)
        try:
            db = self.client.get_default_database()
        except ConfigurationError:
            pass
        else:
            warnings.warn(
                'Database: %s in URI will not work' % db,
                SyntaxWarning, stacklevel=2)

    def register_model(self, model_cls):
        """Decorator for registering model."""
        if not getattr(model_cls, '_database_'):
            raise ModelAttributeError('_database_ missing on %s!' % model_cls.__name__)
        if not getattr(model_cls, '_collection_'):
            raise ModelAttributeError('_collection_ missing on %s!' % model_cls.__name__)

        model_cls._mongo_client_ = self.client

        logging.info('Registering Model ' + model_cls.__name__)
        return model_cls

    def enable_counter(self, base=None, database='counter', collection='counters'):
        """Register the builtin counter model, return the registered Counter
        class and the corresponding ``CounterMixin`` class.

        The ``CounterMixin`` automatically increases and decreases the counter
        after model creation(save without ``_id``) and deletion.

        It contains a classmethod ``count()`` which returns the current count
        of the model collection."""
        Counter._database_ = database
        Counter._collection_ = collection
        bases = (base, Counter) if base else (Counter,)
        counter = self.register_model(type('Counter', bases, {}))

        class CounterMixin(object):
            """Mixin class for model"""
            @classmethod
            def inc_counter(cls):
                """Wrapper for ``Counter.increase()``."""
                return counter.increase(cls._collection_)

            @classmethod
            def dec_counter(cls):
                """Wrapper for ``Counter.decrease()``."""
                return counter.decrease(cls._collection_)

            @classmethod
            def chg_counter(cls, *args, **kwargs):
                """Wrapper for ``Counter.change_by()``."""
                return counter.change_by(cls._collection_, *args, **kwargs)

            @classmethod
            def set_counter(cls, *args, **kwargs):
                """Wrapper for ``Counter.set_to()``."""
                return counter.set_to(cls._collection_, *args, **kwargs)

            def on_save(self, old_dict):
                super(CounterMixin, self).on_save(old_dict)
                if not old_dict.get('_id'):
                    counter.increase(self._collection_)

            def on_delete(self, *args, **kwargs):
                super(CounterMixin, self).on_delete(*args, **kwargs)
                counter.decrease(self._collection_)

            @classmethod
            def count(cls):
                """Return the current count of this collection."""
                return counter.count(cls._collection_)

        logging.info('Counter enabled on: %s' % counter.collection)
        return counter, CounterMixin


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
    _mongo_client_ = None
    _database_ = None
    _collection_ = None
    _defaults_ = {}

    @class_property
    def collection(self):
        if not self._mongo_client_:
            raise ModelAttributeError('collection is available after registration!')
        return getattr(self._mongo_client_[self._database_], self._collection_)

    def __new__(cls, *args, **kwargs):
        """set defaults for instance of model"""
        # merge _defaults_ from base classes
        defaults = {}
        for b_cls in cls.__bases__:
            defaults.update(getattr(b_cls, '_defaults_', {}))

        # override with subclass's _defaults_
        defaults.update(getattr(cls, '_defaults_', {}))
        cls._defaults_ = defaults

        # set default to instance
        instance = super(Model, cls).__new__(cls, *args, **kwargs)
        for k, v in cls._defaults_.items():
            value = v() if isinstance(v, Callable) else v
            instance.setdefault(k, value)

        return instance

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, super(Model, self).__repr__())

    @classmethod
    def by_id(cls, oid):
        """Find a model object by its ``ObjectId``,
        ``oid`` can be string or ObjectId"""
        if oid:
            d = cls.collection.find_one(ObjectId(oid))
            if d:
                return cls(**d)

    @classmethod
    def delete_by_id(cls, oid):
        """Delete a document from collection by its ``ObjectId``,
        ``oid`` can be string or ObjectId"""
        if oid:
            cls.collection.remove(ObjectId(oid))

    @classmethod
    def from_dict(cls, d):
        """Build model object from a dict. Will be removed in v1.0"""
        warnings.warn(
            'from_dict is deprecated and will be removed in v1.0!',
            stacklevel=2)
        d = d or {}
        return cls(**d)

    @classmethod
    def from_cursor(cls, cursor):
        """Build model object from a pymongo cursor."""
        for d in cursor:
            yield cls(**d)

    @classmethod
    def find(cls, *args, **kwargs):
        """Same as ``collection.find``, return model object instead of simple dict."""
        return cls.from_cursor(cls.collection.find(*args, **kwargs))

    @classmethod
    def find_one(cls, *args, **kwargs):
        """Same as ``collection.find_one``, return model object instead of simple dict."""
        d = cls.collection.find_one(*args, **kwargs)
        if d:
            return cls(**d)

    @property
    def id(self):
        """String representation of attribute ``_id``."""
        if '_id' in self:
            return str(self._id)

    def reload(self, d=None):
        """Reload model from given dict or database."""
        if d:
            self.clear()
            self.update(d)
        elif self.id:
            new_dict = self.by_id(self._id)
            self.clear()
            self.update(new_dict)
        else:
            # should I raise an exception here?
            # Like "Model must be saved first."
            pass

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
        """Hook after delete successful."""
        pass

    def delete(self):
        """Remove from database."""
        if not self.id:
            return
        self.collection.remove({'_id': self._id})
        self.on_delete(self)


class Counter(Model):
    """Builtin counter model."""
    @classmethod
    def set_to(cls, name, num):
        """Set counter of ``name`` to ``num``."""
        if num < 0:
            raise CounterValueError('Counter[%s] can not be set to %s' % (name, num))
        else:
            counter = cls.collection.find_and_modify(
                {'name': name},
                {'$set': {'seq': num}},
                new=True,
                upsert=True
            )
            return counter['seq']

    @classmethod
    def change_by(cls, name, num):
        """Change counter of ``name`` by ``num`` (can be negative)."""
        count = cls.count(name)
        if count + num < 0:
            raise CounterValueError('Counter[%s] will be negative after %+d.' % (name, num))

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


class MonguException(Exception):
    """Base class for exceptions from mongu."""
    pass


class ModelAttributeError(MonguException):
    pass


class CounterValueError(MonguException):
    pass