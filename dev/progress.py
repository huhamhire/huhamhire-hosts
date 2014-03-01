#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys
import time


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


class Progress(object):
    __line_width = 79
    _counter = None
    _timer = None

    @classmethod
    def set_counter(cls, counter):
        cls._counter = counter

    @classmethod
    def set_timer(cls, timer):
        cls._timer = timer

    @classmethod
    def show_status(cls, message, status, error=0):
        msg_len = cls.__line_width - 20
        status = status.center(11)
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
        count = cls._counter.count
        total = cls._counter.total

        count_len = len(str(total))
        eta_len = 9

        prog_len = cls.__line_width - 2 * count_len - eta_len - 6

        prog = 1.0 * prog_len * count / total
        bar = ''.join(['=' * int(prog), '-' * int(2 * prog % 2)])
        bar = bar.ljust(prog_len)

        # Get ETA
        timer = cls._timer
        eta = "ETA " + timer.format(timer.eta(count, total))

        count = str(count).rjust(count_len)
        total = str(total).rjust(count_len)
        progress_bar = "%s/%s: [%s] %s" % (count, total, bar, eta)
        sys.stdout.write("\r" + progress_bar)

    @classmethod
    def show_message(cls, message):
        sys.stdout.write("\r" + " " * cls.__line_width +
                         "\r> " + message + "\n")

    @classmethod
    def dash(cls):
        sys.stdout.write("\r" + " " * cls.__line_width +
                         "\r" + "-" * cls.__line_width + "\n")