# Introducing to Mongu
**Mongu** is yet another Python Object-Document Mapper on top of ``PyMongo``. It's lightweight, intuitive to use and easy to understand.

- If you want **control**.
- If you really care about **performance**.
- If those **heavy and slow layers** have nothing or more than you need.

Well, **Mongu** maybe the one for you.

You are the only one who knows what you reall need.

Therefor **Mongu** does nothing but a skeleton for you to fill.

Actually, if you have ever tried to write your own ODM, you may already implemented parts of **Mongu** :D

# Installation
	pip install mongu

# Dependences
- pymongo >= 2.7

*Older(not ancient) version should work just fine, but 2.7 is tested.*

# Documentation
## A really quick example

    @register_model
    class User(Model):
        _database_   = 'test'
        _collection_ = 'users'
        _defaults_   = {'is_activated': False}  # default attribute

    >> user = User(name='Mongu')
    User({'name': 'Mongu', 'is_activated': False})
    >> user.save()
    User({'name': 'Mongu', 'is_activated': True, '_id': ObjectId('534f81bd7246ef6955d2388f')})

For more detailed examples and API: http://mongu.readthedocs.org

# License
Code and documentation are available according to the MIT License.

# Send feedback!
If you thought **Mongu** is helpful, please [tell me](mailto:mail2tevin@gmail.com), a brif message like “This is what I always wanted” is enough, I would love to know!

Of course by all means feel free to send pull requests or create issues, it's welcomed.

Thanks!
