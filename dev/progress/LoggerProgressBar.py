#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *


class LoggerProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super(LoggerProgressBar, self).__init__(parent)

        self.setAlignment(Qt.AlignHCenter)
        self.setValue(0)
        self.setFormat("")

    @pyqtSlot(int, int, str)
    def set_progress(self, count, total, eta):
        self.setMaximum(total)
        self.setValue(count)
        self.setFormat("%v / %m ETA " + eta)
