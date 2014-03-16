#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys

from util import ProgressModel


class Progress(ProgressModel):

    @classmethod
    def show_status(cls, message, status, error=0):
        msgs = cls._split_message(message)
        msg_lines = cls._set_message_lines(msgs, status)
        for i, line in enumerate(msg_lines):
            msg_lines[i] = "\r%s\n" % line
        out_msg = "\r" + " " * cls._line_width + "".join(msg_lines)
        if not error:
            sys.stdout.write(out_msg)
        else:
            sys.stderr.write(out_msg)

    @classmethod
    def progress_bar(cls):
        count = cls._counter.count
        total = cls._counter.total

        count_len = len(str(total))
        eta_len = 9

        prog_len = cls._line_width - 2 * count_len - eta_len - 6

        prog = cls._get_progress()
        bar = ''.join(['=' * int(prog), '-' * int(2 * prog % 2)])
        bar = bar.ljust(prog_len)

        # Get ETA
        eta = cls._get_eta()

        count = str(count).rjust(count_len)
        total = str(total).rjust(count_len)
        progress_bar = "%s/%s: [%s] %s" % (count, total, bar, eta)
        sys.stdout.write("\r" + progress_bar)

    @classmethod
    def show_message(cls, message):
        sys.stdout.write("\r" + " " * cls._line_width +
                         "\r> " + message + "\n")

    @classmethod
    def dash(cls):
        sys.stdout.write("\r" + " " * cls._line_width +
                         "\r" + "-" * cls._line_width + "\n")