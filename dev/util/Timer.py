#!/usr/bin/env python
# -*- coding: utf-8 -*
import time


class Timer(object):
    start_time = None

    def __init__(self, start_time):
        self.start_time = start_time

    def timer(self):
        return time.time() - self.start_time

    @staticmethod
    def format(t):
        s = int(t)
        seconds = s % 60
        m = s // 60
        minutes = m % 60
        h = m // 60
        return "%02d:%02d:%02d" % (h, minutes, seconds)

    @staticmethod
    def format_utc(t):
        return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(t))

    def eta(self, done, total):
        max_eta = 100 * 60 * 60 - 1
        if done < 2:
            return max_eta
        else:
            eta = self.timer() * (total - done) / done
            if eta > max_eta:
                return max_eta
            else:
                return eta
