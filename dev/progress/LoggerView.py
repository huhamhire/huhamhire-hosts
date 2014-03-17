#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from LoggerUIColors import LoggerUIColors


class LoggerView(QTextEdit):
    mutex = threading.Lock()

    def __init__(self, parent=None):
        super(LoggerView, self).__init__(parent)

        self.document().setMaximumBlockCount(3000)
        self.setCursorWidth(2)
        self.setReadOnly(True)
        self.setTextColor(LoggerUIColors.NormalText)
        self.viewport().setCursor(Qt.ArrowCursor)
        self.cursorPositionChanged.connect(self.highlight_selected_line)

        # Set background color and selection color
        palette = self.palette()
        palette.setColor(QPalette().Base, LoggerUIColors.EditorBackground)
        palette.setColor(
            QPalette().Highlight, LoggerUIColors.SelectionBackground)
        palette.setColor(
            QPalette().HighlightedText, LoggerUIColors.SelectionText)
        self.setPalette(palette)

        # Set default font
        self.setCurrentFont(QFont("Consolas", 11))

    @pyqtSlot(list)
    def append_okay_lines(self, lines):
        self.setTextColor(LoggerUIColors.OkayText)
        self._append_lines(lines)
        self.setTextColor(LoggerUIColors.NormalText)

    @pyqtSlot(list)
    def append_error_lines(self, lines):
        self.setTextColor(LoggerUIColors.ErrorText)
        self._append_lines(lines)
        self.setTextColor(LoggerUIColors.NormalText)

    @pyqtSlot(list)
    def append_normal_lines(self, lines):
        self.setTextColor(LoggerUIColors.NormalText)
        self._append_lines(lines)

    def _append_lines(self, lines):
        self.mutex.acquire()
        for line in lines:
            self.append(line)
        self.mutex.release()

    @pyqtSlot()
    def highlight_selected_line(self):
        self.setExtraSelections([])

        highlight = QTextEdit.ExtraSelection()
        highlight.cursor = self.textCursor()
        highlight.format.setProperty(QTextFormat().FullWidthSelection, True)
        highlight.format.setBackground(LoggerUIColors.SelectionBackground)

        extras = self.extraSelections()
        extras.append(highlight)
        self.setExtraSelections(extras)