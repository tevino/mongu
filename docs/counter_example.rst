Example of using builtin ``Counter`` and ``CounterMixin``
=========================================================

We don't assume you are stupid::

    >> from mongu import enable_counter

    >> Counter, CounterMixin = enable_counter()

**Define a Model with CounterMixin**::

    >> @register_model
    >> class User(CounterMixin, Model):  # order of base classes matters
    >>     _database_   = 'test'
    >>     _collection_ = 'users'


**How to use builtin ``Counter`` and `CounterMixin`**::

    >> for name in ('Builtin', 'Counter', 'Test'):
    >>     User(username=name).save()  # counter increases after creation
    >> User.count()                    # provided by ``CounterMixin``
    3
    >> User.find_one().delete()        # counter decreases adter deletion
    >> User.count()
    2

**Use Counter independently**::

    >> Counter.count('girlfriend')            # You born alone :|
    0

    >> Counter.increase('girlfriend')         # Before you find your first love :D
    1
    >> Counter.decrease('girlfriend')         # then you went through the very first break-up :(
    0

    >> Counter.change_by('girlfriend', 100)   # Oneday you had a crazy dream :P
    100
    >> Counter.change_by('girlfriend', -100)  # you woke up, everything turns to dust :(
    0

    >> Counter.count('girlfriend')            # Still dreaming? Check it again! 0_0
    0

So sad, right?

Use **Mongu** to write your own story!
