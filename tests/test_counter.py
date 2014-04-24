# -*- coding: utf-8 -*-
from .base import CounterTestCase
from random import randint


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
        self.assertRaises(Exception, self.Counter.set_to, k, -r)

    def test_base(self):
        # `increase_by_6` is implemented in the base class
        self.assertEqual(self.Counter.increase_by_6('Final'), 6)

    def test_exception(self):
        # TODO: assert custom exception
        self.assertRaises(Exception, self.Counter.change_by, 'exception', -100)
