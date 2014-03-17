#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import *

from LoggerHandler import LoggerHandler
from LoggerView import LoggerView
from LoggerProgressBar import LoggerProgressBar


class ProgressWidget(QWidget):

    def __init__(self, *args):
        super(ProgressWidget, self).__init__(*args)

        self.resize(800, 640)

        self.view = LoggerView(self)
        self.logger = LoggerHandler(self)
        self.progress = LoggerProgressBar(self)

        self.logger.normal_message.connect(self.view.append_normal_lines)
        self.logger.okay_message.connect(self.view.append_okay_lines)
        self.logger.error_message.connect(self.view.append_error_lines)
        self.logger.update_progress.connect(self.progress.set_progress)

        layout = QVBoxLayout(self)
        layout.setMargin(5)
        layout.addWidget(self.view)
        layout.addWidget(self.progress)
        self.setLayout(layout)