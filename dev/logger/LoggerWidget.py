#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import *

from LoggerView import LoggerView


class LoggerWidget(QWidget):
    def __init__(self, *args):
        super(LoggerWidget, self).__init__(*args)

        self.resize(800, 640)

        self.logger_view = LoggerView(self)

        layout = QVBoxLayout(self)
        layout.setMargin(5)
        layout.addWidget(self.logger_view)
        self.setLayout(layout)
