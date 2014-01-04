#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import *

from HostsEditorLexer import HostsSciLexer


class TextEditor(QsciScintilla):
    def __init__(self, parent=None):
        super(TextEditor, self).__init__(parent)

        self.lexer = HostsSciLexer(self)
        self.setLexer(self.lexer)

        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, 10)
        self.setMarginsForegroundColor(QColor("#868686"))
        self.setMarginsBackgroundColor(QColor("#272822"))

        self.setUtf8(True)
        self.setEolMode(self.EolUnix)
        self.setEolVisibility(False)

        self.setFolding(self.PlainFoldStyle, 2)
        self.setFoldMarginColors(QColor("#272822"), QColor("#272822"))

        self.setWrapMode(self.WrapWord)
        self.setWrapIndentMode(self.WrapIndentSame)
        self.setWrapVisualFlags(self.WrapFlagInMargin)

        self.setBraceMatching(self.SloppyBraceMatch)
        self.setMatchedBraceForegroundColor(QColor("#F8F8F2"))
        self.setMatchedBraceBackgroundColor(QColor("#3A6DA0"))

        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#3E3D32"))
        self.setCaretWidth(2)
        self.setCaretForegroundColor(QColor("#F8F8F0"))

        self.setSelectionBackgroundColor(QColor("#3E3D32"))
        self.setSelectionToEol(True)

        self.setAutoIndent(True)
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setIndentationGuides(True)
        self.setIndentationGuidesBackgroundColor(QColor("#868686"))
        self.setTabWidth(4)
        self.setWhitespaceVisibility(self.WsInvisible)

        self.setEdgeColor(QColor("#868686"))
        self.setEdgeColumn(80)
        self.setEdgeMode(self.EdgeLine)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.SendScintilla(self.SCI_EMPTYUNDOBUFFER)


class EditorWidget(QWidget):
    def __init__(self, parent=None, *args):
        super(EditorWidget, self).__init__(parent, *args)
        self.resize(800, 640)

        self.editor = TextEditor(self)
        self.editor.cursorPositionChanged.connect(self.on_cursor_changed)
        self.editor.verticalScrollBar().valueChanged.connect(
            self.update_screen_style)
        self.editor.linesChanged.connect(self.on_lines_changed)

        layout = QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.editor)
        self.setLayout(layout)

    @pyqtSlot(int)
    def update_screen_style(self, start_line):
        # Update style of visible text
        start_pos = self.editor.positionFromLineIndex(start_line, 0)
        visible = self.editor.SendScintilla(QsciScintilla.SCI_LINESONSCREEN)
        end_line = start_line + visible
        end_line_len = self.editor.lineLength(end_line)
        while end_line_len == -1:
            end_line -= 1
            end_line_len = self.editor.lineLength(end_line)
        end_pos = self.editor.positionFromLineIndex(end_line, end_line_len)
        self.editor.lexer.styleText(start_pos, end_pos)

    @pyqtSlot()
    def on_lines_changed(self):
        self.editor.lexer.styleText(0, len(self.editor.text()))

    @pyqtSlot()
    def on_cursor_changed(self):
        # Adjust line number margin width
        line_count = self.editor.lines()
        line_width = len(str(line_count)) * 10 + 1
        if line_width > self.editor.marginWidth(1):
            self.editor.setMarginWidth(1, line_width)

        # Update style of visible text
        start_line = self.editor.firstVisibleLine()
        self.update_screen_style(start_line)


def main():
    app = QApplication(sys.argv)
    w = EditorWidget()

    code_file = open("C:/Windows/System32/drivers/etc/hosts", "r")
    # code_file = open("E:/Project/Hosts/example.hosts", "r")
    try:
        text = ''.join(code_file.readlines())
    finally:
        code_file.close()

    w.editor.setText(text)

    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
