.. Mongu documentation master file, created by
   sphinx-quickstart on Thu Apr 17 10:14:31 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introducing to Mongu
========================================
**Mongu** is yet another Python Object-Document Mapper on top of ``PyMongo``. It's lightweight, intuitive to use and easy to understand.

- If you want **control**.
- If you really care about **performance**.
- If those **heavy and slow layers** have nothing or more than you need.

Well, **Mongu** maybe the one for you.

You are the only one who knows what you reall need.

Therefor **Mongu** does nothing but a skeleton for you to fill.

Actually, if you have ever tried to write your own ODM, you may already implemented parts of **Mongu** :D


You don't need user-guides but examples to get started.
========================================================

We don't assume you are stupid, here we go::

    from mongu import set_database, register_model, Model

    set_database('test') # set database before anything else

**Model definition**::

    @register_model
    class User(Model):
        _collection_ = 'users'                # collection name
        _defaults_ = {'is_activated': False}  # default attribute

        def activate(self):                   # a custom method
            self.is_activated = True

**Basic manipulation**

The model is a dict::

    >> user = User(username='Mongu')
    >> user
    User({'username': 'Mongu', 'is_activated': False})
    >> 'username' in user
    True

With your methods::

    >> user.activate()

That work::

    >> user
    User({'username': 'Mongu', 'is_activated': True})
    >> user.save()
    >> user
    User({'username': 'Mongu', 'is_activated': True, '_id': ObjectId('534f81bd7246ef6955d2388f')})

``ObjectId`` won't be a pain::

    >> repr(user._id)
    "ObjectId('534f81bd7246ef6955d2388f')"
    >> repr(user.id)
    "534f81bd7246ef6955d2388f"

You can find by ``str`` or ``ObjectId``, The following two lines get the same result::

    >> User.by_id(user._id)
    >> User.by_id(user.id)
    User({u'username': u'Mongu', u'is_activated': True, u'_id': ObjectId('534f81bd7246ef6955d2388f')})


**Query** (It's really just ``PyMongo``)

Create some users::

    >> for name in ('Mongu', 'Rocks'):
    >>    User(username=name).save()
    >> list(User.find())
    [User({u'username': u'Mongu', u'is_activated': False, u'_id': ObjectId('534f87c27246ef95a3294c28')}),
     User({u'username': u'Rocks', u'is_activated': False, u'_id': ObjectId('534f87c27246ef95a3294c29')})]

It's naked ``PyMongo``, nothing hidden from you::

    >> User.collection
    Collection(Database(MongoClient('localhost', 27017), u'test'), u'users')

``PyMongo`` raw query::

    >> user_naked = User.collection.find_one({'username': 'Rocks'})

Use ``Mongu`` to dress up::

    >> user_dressed = User.find_one({'username': 'Rocks'})

Differences::

    >> user_dressed.activate()
    >> user_naked.activate()  # this will raise an AttributeError

You konw Why::

    >> type(user_naked)
    <type 'dict'>
    >> type(user_dressed)
    <class '__main__.User'>


API References
===============

Basic:
-------

.. automodule:: mongu
   :members: set_database, register_model, enable_counter


Extra
------

.. automodule:: mongu
   :members: get_connection, , ObjectDict


Base Model:
--------------

.. autoclass:: mongu.Model
   :members:
   :member-order: bysource


Builtin Counter:
------------------------

For more information: `What and Why
<http://docs.mongodb.org/manual/tutorial/create-an-auto-incrementing-field/#auto-increment-counters-collection>`_

.. autoclass:: mongu.Counter
   :members:
   :member-order: bysource


.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

