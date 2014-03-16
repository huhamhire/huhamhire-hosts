#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from LoggerColors import LoggerColors


class LoggerView(QTextEdit):

    def __init__(self, parent=None):
        super(LoggerView, self).__init__(parent)

        self.document().setMaximumBlockCount(3000)
        self.setCursorWidth(2)
        self.setReadOnly(True)
        self.setTextColor(LoggerColors.NormalText)
        self.viewport().setCursor(Qt.ArrowCursor)
        self.cursorPositionChanged.connect(self.highlight_selected_line)

        # Set background color and selection color
        palette = self.palette()
        palette.setColor(QPalette().Base, LoggerColors.EditorBackground)
        palette.setColor(
            QPalette().Highlight, LoggerColors.SelectionBackground)
        palette.setColor(
            QPalette().HighlightedText, LoggerColors.SelectionText)
        self.setPalette(palette)

        # Set default font
        self.setCurrentFont(QFont("Consolas", 11))

    @pyqtSlot(QString)
    def append_okay_message(self, message):
        self.setTextColor(LoggerColors.OkayText)
        self.append(message)
        self.setTextColor(LoggerColors.NormalText)

    @pyqtSlot(QString)
    def append_error_message(self, message):
        self.setTextColor(LoggerColors.ErrorText)
        self.append(message)
        self.setTextColor(LoggerColors.NormalText)

    @pyqtSlot(QString)
    def append_normal_message(self, message):
        self.setTextColor(LoggerColors.NormalText)
        self.append(message)

    @pyqtSlot()
    def highlight_selected_line(self):
        self.setExtraSelections([])

        highlight = QTextEdit.ExtraSelection()
        highlight.cursor = self.textCursor()
        highlight.format.setProperty(QTextFormat().FullWidthSelection, True)
        highlight.format.setBackground(LoggerColors.SelectionBackground)

        extras = self.extraSelections()
        extras.append(highlight)
        self.setExtraSelections(extras)