# -*- coding: utf-8 -*-

from IPy import IP

from PyQt4.Qsci import QsciLexerCustom, QsciScintilla
from PyQt4.QtCore import QString
from PyQt4.QtGui import QColor, QFont


class HostsSciLexer(QsciLexerCustom):
    def __init__(self, parent=None):
        super(HostsSciLexer, self).__init__(parent)
        self.setEditor(parent)

    def autoIndentStyle(self):
        return QsciScintilla.AiClosing

    def defaultColor(self, style=None):
        if style == self.Comment:
            return QColor("#75715E")
        elif style == self.IPAddress:
            return QColor("#AE81FF")
        elif style == self.DomainName:
            return QColor("#FD971F")
        elif style == self.Operator:
            return QColor("#F92672")
        elif style == self.Section:
            return QColor("#66D9EF")
        elif style == self.SectionName:
            return QColor("#A6E22E")
        elif style == self.Keyword:
            return QColor("#F92672")
        elif style == self.InValid:
            return QColor("#F92672")
        return QColor("#F8F8F2")

    def defaultEolFill(self, style):
        return False

    def defaultFont(self, style=None):
        font = QFont("Consolas", 11)
        if style == self.Section:
            font.setItalic(True)
            return font
        return font

    def defaultPaper(self, style=None):
        return QColor("#272822")

    def description(self, style):
        if style == self.Default:
            return QString("Default")
        elif style == self.Comment:
            return QString("Comment")
        elif style == self.IPAddress:
            return QString("IPAddress")
        elif style == self.DomainName:
            return QString("DomainName")
        elif style == self.Operator:
            return QString("Operator")
        elif style == self.Section:
            return QString("Section")
        elif style == self.SectionName:
            return QString("SectionName")
        elif style == self.Keyword:
            return QString("Keyword")
        elif style == self.InValid:
            return QString("InValid")
        return QString()

    def keywords(self, key_set):
        if key_set == 0:
            return "section module"
        elif key_set == 1:
            return "start end"
        elif key_set == 2:
            return "version"
        else:
            return None

    def language(self):
        return "hosts"

    def lexer(self):
        return "HostsSciLexer"

    def styleText(self, start, end):
        editor = self.editor()
        if editor is None:
            return

        sci = editor.SendScintilla
        get_fold_level = editor.SCI_GETFOLDLEVEL
        set_fold_level = editor.SCI_SETFOLDLEVEL
        header_flag = editor.SC_FOLDLEVELHEADERFLAG
        level_base = editor.SC_FOLDLEVELBASE
        number_mask = editor.SC_FOLDLEVELNUMBERMASK
        white_flag = editor.SC_FOLDLEVELWHITEFLAG

        source = ''
        if end > editor.length():
            end = editor.length()
        if end > start:
            source = bytearray(end - start)
            sci(editor.SCI_GETTEXTRANGE, start, end, source)
        if not source:
            return

        index = sci(editor.SCI_LINEFROMPOSITION, start)
        if index > 0:
            pos = sci(editor.SCI_GETLINEENDPOSITION, index - 1)
            prev_state = sci(editor.SCI_GETSTYLEAT, pos)
        else:
            prev_state = self.Default

        self.startStyling(start, 0x1f)

        for line in source.splitlines(True):
            level = sci(get_fold_level, index)
            if line.startswith('#'):
                line_styles = self.set_comment_line_style(line)
            else:
                line_styles = self.set_hosts_line_style(line)

            for style in line_styles:
                self.setStyling(style["len"], style["style"])

            if line_styles[0]["style"] == self.Section:
                if line[line_styles[0]["len"]+1:].lower().startswith("end")\
                        and line_styles[1]["style"] == self.Keyword:
                    level -= 1
                else:
                    level += 1
            else:
                level |= header_flag
            index += 1
            sci(set_fold_level, index, level)

    def set_hosts_line_style(self, line):
        styles = []
        comments = line.split("#", 1)
        if len(comments) > 1:
            comment_styles = self.set_inline_comment_style(comments[1])
        else:
            comment_styles = {}

        line_len = len(comments[0])
        parts = comments[0].split()
        if not len(parts):
            styles.append({"len": line_len, "style": self.Default})
            return styles

        address = str(parts[0])
        add_len = 0
        try:
            add_len = len(address)
            if IP(address).version() in [4, 6]:
                styles.append({"len": add_len, "style": self.IPAddress})
        except ValueError:
            styles.append({"len": add_len, "style": self.InValid})
        finally:
            hosts = comments[0][add_len: line_len]
            styles.extend(self.set_hosts_style(hosts))

        styles.extend(comment_styles)
        return styles

    def set_hosts_style(self, hosts):
        styles = []
        domains = hosts.split(" ")
        for i, domain in enumerate(domains):
            if not domain and i < len(domains) - 1:
                styles.append({"len": 1, "style": self.Default})
                continue
            sects = domain.split(".")
            len_sects = len(sects)
            for j, sect in enumerate(sects):
                if j == 0 or (len_sects > 3 and j in [0, 1]):
                    sect_style = self.DomainName
                else:
                    sect_style = self.Default
                styles.append({"len": len(sect), "style": sect_style})
                if j < len_sects - 1:
                    styles.append({"len": 1, "style": self.Operator})
            if i < len(domains) - 1:
                styles.append({"len": 1, "style": self.Default})
        return styles

    def set_comment_line_style(self, line):
        styles = []
        line_len = len(line)

        words = line.split(" ")
        if len(words) > 1 and words[1].lower().replace(":", "") \
                in self.keywords(0).split():
            styles = self.set_section_line_style(line)
        else:
            styles.append({"len": line_len, "style": self.Comment})
        return styles

    def set_inline_comment_style(self, line_piece):
        line_len = len(line_piece) + 1
        return [{"len": line_len, "style": self.Comment}]

    def set_section_line_style(self, line):
        styles = []
        line_len = len(line)

        parts = line.split(":", 1)
        sec_len = len(parts[0])
        sec_words = parts[0].split(" ")
        word = " ".join([str(word) for word in sec_words[:2]])
        word_len = len(word)
        styles.append(
            {"len": word_len, "style": self.Section})
        if len(sec_words) > 2:
            word = sec_words[2].lower().replace("\n", "")
            if word in self.keywords(1).split():
                word_style = self.Keyword
            else:
                word_style = self.SectionName
            styles.append({"len": sec_len - word_len, "style": word_style})
        if len(parts) > 1:
            styles.append({"len": 1, "style": self.Operator})
            sec_len += 1
        styles.append({"len": line_len - sec_len, "style": self.SectionName})
        return styles

    def writeProperties(self, settings, prefix):
        return False

    Default = 0
    Comment = 1
    IPAddress = 2
    DomainName = 3
    Operator = 4
    Section = 5
    SectionName = 6
    Keyword = 7
    InValid = 8