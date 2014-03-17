#!/usr/bin/env python
# -*- coding: utf-8 -*


class ProgressHandler(object):
    _line_width = 79
    _status_width = 11

    def __init__(self, counter, timer, logger):
        self._counter = counter
        self._timer = timer
        self._logger = logger

    def update_status(self, message, status, error=0):
        msgs = self._split_message(message)
        msg_lines = self._set_message_lines(msgs, status)
        if error:
            for line in msg_lines:
                self._logger.log_err(line)
        else:
            for line in msg_lines:
                self._logger.log_ok(line)

    def _split_message(self, message):
        msg_len = self._line_width - 20
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

    def _set_message_lines(self, msgs, status):
        status = status.center(self._status_width)
        msg_len = self._line_width - 20
        msg_lines = []

        for i, msg in enumerate(msgs):
            if i < len(msgs)-1:
                msg_lines.append(msg)
            elif len(msg) > msg_len:
                msg_lines.append(msg.ljust(msg_len+10+2))
                msg_lines.append(("[%s]" % status).rjust(self._line_width))
            else:
                msg_lines.append(msg.ljust(msg_len) +
                                 ("[%s]" % status).rjust(20))
        return msg_lines

    def update_progress(self):
        counter = self._counter
        eta = self._get_eta()
        self._logger.set_progress(counter, eta)

    def _get_eta(self):
        timer = self._timer
        counter = self._counter
        return "ETA " + timer.format(timer.eta(counter.count, counter.total))

    def update_message(self, message):
        self._logger.log_normal([message])

    def update_dash(self):
        self._logger.log_normal(["-" * self._line_width])