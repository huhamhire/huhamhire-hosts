#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys


class Progress(object):
    __line_width = 78
    _total = 0

    @classmethod
    def set_total(cls, total):
        cls._total = total

    @classmethod
    def status(cls, message, status, error=0):
        msg = "\r%s" % message.ljust(cls.__line_width - 20) \
              + ("[%s]" % status).rjust(20) + "\n"
        if not error:
            sys.stdout.write(msg)
        else:
            sys.stderr.write(msg)

    @classmethod
    def progress_bar(cls, done_count):
        prog_len = cls.__line_width - 20
        prog = 1.0 * prog_len * done_count / cls._total
        bar = ''.join(['=' * int(prog), '-' * int(2 * prog % 2)])
        bar = bar.ljust(prog_len)
        count = str(done_count).rjust(7)
        total = str(cls._total).rjust(7)
        progress_bar = "[%s] %s | %s" % (bar, count, total)
        sys.stdout.write("\r" + progress_bar)