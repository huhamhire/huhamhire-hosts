#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys


class Progress(object):
    __line_width = 78
    _total = 0
    _counter_set = {}

    @classmethod
    def set_total(cls, total):
        cls._total = total

    @classmethod
    def set_counter(cls, counter_set):
        cls._counter_set = counter_set

    @classmethod
    def show_status(cls, message, status, error=0):
        msg_len = cls.__line_width - 20
        msgs = []
        if len(message) >= msg_len:
            messages = message.split(" - ", 1)
            while len(messages[0]) > msg_len+10:
                msgs.append(messages[0][:msg_len+10])
                messages[0] = " " * 6 + messages[0][msg_len+10:]
            if len(messages) == 2:
                last_msg = messages[0] + " - " + messages[1]
                if len(last_msg) > msg_len:
                    msgs.append(messages[0])
                    msgs.append(" " * 6 + "- " + messages[1])
                else:
                    msgs.append(last_msg)
            else:
                msgs.append(messages[0])
        else:
            msgs.append(message)

        for i, msg in enumerate(msgs):
            if i < len(msgs)-1:
                msgs[i] = "\r%s\n" % msg.ljust(msg_len+10+2)
            elif len(msg) > msg_len:
                msgs[i] = "\r%s\n" % msg.ljust(msg_len+10+2) + \
                          ("[%s]" % status).rjust(cls.__line_width) + "\n"
            else:
                msgs[i] = "\r%s" % msg.ljust(msg_len) + \
                          ("[%s]" % status).rjust(20) + "\n"

        out_msg = "\r" + " " * cls.__line_width + "".join(msgs)
        if not error:
            sys.stdout.write(out_msg)
        else:
            sys.stderr.write(out_msg)

    @classmethod
    def progress_bar(cls):
        finish_count = len(cls._counter_set)
        prog_len = cls.__line_width - 20
        prog = 1.0 * prog_len * finish_count / cls._total
        bar = ''.join(['=' * int(prog), '-' * int(2 * prog % 2)])
        bar = bar.ljust(prog_len)
        count = str(finish_count).rjust(7)
        total = str(cls._total).rjust(7)
        progress_bar = "[%s] %s | %s" % (bar, count, total)
        sys.stdout.write("\r" + progress_bar)
