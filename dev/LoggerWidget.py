#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

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


class LoggerWidget(QWidget):
    def __init__(self, *args):
        super(LoggerWidget, self).__init__(*args)

        self.resize(800, 640)

        self.logger_view = LoggerView(self)

        layout = QVBoxLayout(self)
        layout.setMargin(5)
        layout.addWidget(self.logger_view)
        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    w = LoggerWidget()
    test_text(w)
    w.show()
    sys.exit(app.exec_())


def test_text(logger_widget):
    logger_view = logger_widget.logger_view
    logger_view.append_error_message("error")
    logger_view.append_okay_message("ok")
    logger_view.append_normal_message("normal")
    for i in range(1000):
        logger_view.append_okay_message("=" * 80)


if __name__ == "__main__":
    main()