#!/usr/bin/env python
# -*- coding: utf-8 -*


class Counter(object):
    count = 0
    total = 0

    def set_total(self, total):
        self.total = total

    def set_count(self, count):
        self.count = count

    def inc(self):
        self.count += 1

    def dec(self):
        self.count -= 1