#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class LoggerColors(QObject):
    def __init__(self, parent=None):
        super(LoggerColors, self).__init__(parent)

    EditorBackground = QColor("#272822")
    SelectionBackground = QColor("#49483E")
    SelectionText = QColor("#FFFFFF")
    ErrorText = QColor("#FFB3B3")
    OkayText = QColor("#6AE96A")
    NormalText = QColor("#E4E4FF")