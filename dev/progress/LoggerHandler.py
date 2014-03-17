#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *


class LoggerHandler(QObject):
    normal_message = pyqtSignal(list)
    okay_message = pyqtSignal(list)
    error_message = pyqtSignal(list)
    update_progress = pyqtSignal(int, int, str)

    def __init__(self, parent=None):
        super(LoggerHandler, self).__init__(parent)

    def log_normal(self, message):
        self.normal_message.emit(message)

    def log_ok(self, message):
        self.okay_message.emit(message)

    def log_err(self, message):
        self.error_message.emit(message)

    def set_progress(self, count, total, eta):
        self.update_progress.emit(count, total, eta)