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

    def test_increase(self):
        k = 'another'
        self.Counter.increase(k)  # increase by 1
        self.assertEqual(1, self.Counter.count(k))

    def test_decrease(self):
        k = 'decrease'
        self.Counter.increase(k)  # increase by 1
        self.Counter.decrease(k)  # decrease by 1
        self.assertEqual(0, self.Counter.count(k))

    def test_change_by(self):
        k = 'more'
        self.Counter.change_by(k, 3)   # increase by 3
        self.assertEqual(3, self.Counter.count(k))

        count = self.Counter.count(k)
        self.Counter.change_by(k, -1)  # decrease by 1
        self.assertEqual(count - 1, self.Counter.count(k))
