# -*- coding: utf-8 -*-
from random import randint
from mongu import CounterValueError
from .base import CounterTestCase


class CounterTests(CounterTestCase):
    def test_mixin(self):
        for name in ('Builtin', 'Counter', 'Test'):
            u = self.User(username=name)
            u.save()
            u.age = randint(0, 99)
            u.save()
        # counter should only increases after the first save
        self.assertEqual(self.User.count(), 3)

    def test_initial(self):
        self.assertEqual(0, self.Counter.count('something-new'))

    def test_inc_counter(self):
        c = self.User.count()
        self.User.inc_counter()
        self.assertEqual(self.User.count(), c + 1)

    def test_dec_counter(self):
        self.User.inc_counter()
        c = self.User.count()
        self.User.dec_counter()
        self.assertEqual(self.User.count(), c - 1)

    def test_chg_counter(self):
        c = self.User.count()
        self.User.chg_counter(100)
        self.assertEqual(self.User.count(), c + 100)

    def test_set_counter(self):
        self.User.set_counter(77)
        self.assertEqual(self.User.count(), 77)

    def test_increase(self):
        k = 'another'
        self.assertEqual(1, self.Counter.increase(k))  # increase by 1

    def test_decrease(self):
        k = 'decrease'
        self.Counter.increase(k)  # increase by 1
        self.Counter.decrease(k)  # decrease by 1
        self.assertEqual(0, self.Counter.count(k))

    def test_change_by(self):
        k = 'more'
        self.assertEqual(3, self.Counter.change_by(k, 3))       # increase 0 by 3
        self.assertEqual(3 - 1, self.Counter.change_by(k, -1))  # decrease 3 by 1

    def test_set_to(self):
        k = 'test set_to'
        r = randint(0, 100)
        self.Counter.set_to(k, r)
        self.assertEqual(self.Counter.count(k), r)
        self.assertRaises(CounterValueError, self.Counter.set_to, k, -r)

    def test_base(self):
        class CounterBase(object):
            @classmethod
            def increase_by_6(self, key):
                return self.change_by(key, 6)

        Counter, _ = self.client.enable_counter(base=CounterBase)
        self.assertEqual(Counter.increase_by_6('Final'), 6)

    def test_change_by_exception(self):
        self.assertRaises(CounterValueError, self.Counter.change_by, 'exception', -9999)

    def test_on_delete(self):
        user = self.User(username='xx')
        user.save()
        before = self.User.count()
        user.delete()
        self.assertEqual(before - 1, self.User.count())
