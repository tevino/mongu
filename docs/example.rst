Example usage
==============

We don't assume you are stupid, here we go

**Model definition**::

    from mongu import Client, Model

    c = Client()                              # connect to MongoDB

    @c.register_model
    class User(Model):
        _database_   = 'test'                 # database name
        _collection_ = 'users'                # collection name
        _defaults_ = {'is_activated': False}  # default attribute (callable value is supported)

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
