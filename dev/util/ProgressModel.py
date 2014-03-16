#!/usr/bin/env python
# -*- coding: utf-8 -*


class ProgressModel(object):
    _line_width = 79
    _status_width = 11
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
        pass

    @classmethod
    def _split_message(cls, message):
        msg_len = cls._line_width - 20
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
        return msgs

    @classmethod
    def _set_message_lines(cls, msgs, status):
        status = status.center(cls._status_width)
        msg_len = cls._line_width - 20
        msg_lines = []

        for i, msg in enumerate(msgs):
            if i < len(msgs)-1:
                msg_lines.append(msg)
            elif len(msg) > msg_len:
                msg_lines.append(msg.ljust(msg_len+10+2))
                msg_lines.append(("[%s]" % status).rjust(cls._line_width))
            else:
                msg_lines.append(msg.ljust(msg_len) +
                                 ("[%s]" % status).rjust(20))
        return msg_lines

    @classmethod
    def progress_bar(cls):
        pass

    @classmethod
    def _get_progress(cls):
        counter = cls._counter
        return 1.0 * counter.count / counter.total

    @classmethod
    def _get_eta(cls):
        timer = cls._timer
        counter = cls._counter
        return "ETA " + timer.format(timer.eta(counter.count, counter.total))

    @classmethod
    def show_message(cls, message):
        pass

    @classmethod
    def dash(cls):
        pass