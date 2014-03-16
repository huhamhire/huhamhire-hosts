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
        secs = int(t)
        minutes = secs // 60
        seconds = secs % 60
        return "%02d:%02d" % (minutes, seconds)

    @staticmethod
    def format_utc(t):
        return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(t))

    def eta(self, done, total):
        if done < 2:
            return 100 * 60 - 1
        else:
            eta = self.timer() * (total - done) / done
            if eta > 100 * 60 - 1:
                return 100 * 60 - 1
            else:
                return eta