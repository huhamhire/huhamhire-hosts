#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import *

from HostsEditorLexer import HostsSciLexer


class PythonEditorLexer(QsciLexerPython):
    def __init__(self, parent=None):
        """

        @param parent:
        """
        super(PythonEditorLexer, self).__init__(parent)

        self.setDefaultColor(QColor("#F8F8F2"))
        self.setDefaultPaper(QColor("#272822"))

        font = QFont("Consolas", 11)
        # font = QFont("Bitstream Vera Sans Mono", 10)

        self.setDefaultFont(font)
        self.setFont(font, -1)

        self.setColor(QColor("#75715E"), self.Comment)
        self.setColor(QColor("#75715E"), self.TripleDoubleQuotedString)
        self.setColor(QColor("#75715E"), self.TripleSingleQuotedString)
        self.setColor(QColor("#E6DB74"), self.DoubleQuotedString)
        self.setColor(QColor("#E6DB74"), self.SingleQuotedString)
        self.setColor(QColor("#E6DB74"), self.UnclosedString)
        self.setColor(QColor("#AE81FF"), self.Number)
        self.setColor(QColor("#F92672"), self.Keyword)
        self.setColor(QColor("#A6E22E"), self.ClassName)
        self.setColor(QColor("#A6E22E"), self.FunctionMethodName)
        self.setColor(QColor("#A6E22E"), self.Decorator)

        italic_font = QFont(font)
        italic_font.setItalic(True)
        self.setFont(italic_font, self.Keyword)
        self.setFont(italic_font, self.FunctionMethodName)


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

        self.SendScintilla(self.SCI_SETHSCROLLBAR, 0)
        self.SendScintilla(self.SCI_SETWRAPMODE, 1)
        self.SendScintilla(self.SCI_EMPTYUNDOBUFFER)


class EditorWidget(QWidget):
    def __init__(self, parent=None, *args):
        super(EditorWidget, self).__init__(parent, *args)
        self.resize(800, 640)

        # code_file = open("C:/Windows/System32/drivers/etc/hosts", "r")
        code_file = open("E:/Project/Hosts/example.hosts", "r")
        try:
            text = ''.join(code_file.readlines(200))
        finally:
            code_file.close()

        self.editor = TextEditor(self)
        self.editor.textChanged.connect(self.on_text_changed)

        self.editor.setText(text)

        layout = QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.editor)
        self.setLayout(layout)

    @pyqtSlot()
    def on_text_changed(self):
        # Adjust line number margin width
        width = len(str(
            len(self.editor.text().split("\n"))
        ))
        self.editor.setMarginWidth(1, width * 10 + 1)

        # Update text style
        self.editor.lexer.styleText(0, len(self.editor.text()))


def main():
    app = QApplication(sys.argv)
    w = EditorWidget()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
