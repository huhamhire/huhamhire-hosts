#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  qdialog_ui.py : Draw the Graphical User Interface.
#
# Copyleft (C) 2014 - huhamhire hosts team <hosts@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING
# THE WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

import os

from PyQt4 import QtCore, QtGui

import sys

sys.path.append("..")
from util import RetrieveData, CommonUtil
from __version__ import __version__, __release__
from language import LangUtil
from util_ui import Ui_Util, _translate, _fromUtf8

# Path to store language files
LANG_DIR = "./gui/lang/"


class QDialogUI(QtGui.QDialog, object):
    """
    CursesUI class contains methods to draw the Graphical User Interface (GUI)
    of Hosts Setup Utility. The methods to make GUI here are based on
    `PyQT4 <http://pyqt.sourceforge.net/Docs/PyQt4/>`_.

    .. note:: This class is subclass of :class:`QtGui.QDialog` class
        and :class:`object` class.

    :ivar str _cur_ver: Current version of local hosts data file.
    :ivar QtCore.QTranslator _trans: An instance of
        :class:`QtCore.QTranslator` object indicating the current UI language
        setting.

    :ivar QtGui.QApplication app: An instance of :class:`QtGui.QApplication`
        object to launch the Qt application.

    :ivar list mirrors: Dictionaries containing `tag`, `test url`, and
        `update url` of mirror servers.
    :ivar str platform: Platform of current operating system. The value could
        be `Windows`, `Linux`, `Unix`, `OS X`, and of course `Unknown`.
    :ivar bool plat_flag: A flag indicating whether current operating system
        is supported or not.

    :ivar object ui: Form implementation declares layout of the main dialog
        which is generated from a UI file designed by `Qt Designer`.
    :ivar str custom: File name of User Customized Hosts File. Customized
        hosts would be able to select if this file exists. The default file
        name is ``custom.hosts``.

        .. seealso:: :ref:`User Customized Hosts<intro-customize>`.
    """
    _cur_ver = ""
    _trans = None

    app = None
    mirrors = []
    platform = ''
    plat_flag = True
    ui = None

    custom = "custom.hosts"

    def __init__(self):
        """
        Initialize a new instance of this class. Set the UI object and current
        translator of the main dialog.
        """
        self.app = QtGui.QApplication(sys.argv)
        super(QDialogUI, self).__init__()
        self.ui = Ui_Util()
        self.ui.setupUi(self)
        self.set_style()
        self.set_stylesheet()
        # Set default UI language
        trans = QtCore.QTranslator()
        trans.load(LANG_DIR + "en_US")
        self._trans = trans
        self.app.installTranslator(trans)
        self.set_languages()

    def set_stylesheet(self):
        """
        Set the style sheet of main dialog.

        .. seealso:: :ref:`QT Stylesheet<qt-stylesheet>`.
        """
        with open("./gui/theme/default.qss", "r") as qss:
            self.app.setStyleSheet(qss.read())

    def set_style(self):
        """
        Set the main dialog with a window style depending on the os platform.
        """
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        system = self.platform
        if system == "Windows":
            pass
        elif system == "Linux":
            # Set window style for sudo users.
            QtGui.QApplication.setStyle(
                QtGui.QStyleFactory.create("Cleanlooks"))
        elif system == "OS X":
            pass

    def set_languages(self):
        """
        Set optional language selection items in the SelectLang widget.
        """
        self.ui.SelectLang.clear()
        langs = LangUtil.language
        langs_not_found = []
        for locale in langs:
            if not os.path.isfile(LANG_DIR + locale + ".qm"):
                langs_not_found.append(locale)
        for locale in langs_not_found:
            langs.pop(locale)
        LangUtil.language = langs
        if len(langs) <= 1:
            self.ui.SelectLang.setEnabled(False)
            # Block the signal while set the language selecions.
        self.ui.SelectLang.blockSignals(True)
        sys_locale = LangUtil.get_locale()
        if sys_locale not in langs.keys():
            sys_locale = "en_US"
        for i, locale in enumerate(sorted(langs.keys())):
            if sys_locale == locale:
                select = i
            lang = langs[locale]
            self.ui.SelectLang.addItem(_fromUtf8(""))
            self.ui.SelectLang.setItemText(i, lang)
        self.ui.SelectLang.blockSignals(False)
        self.ui.SelectLang.setCurrentIndex(select)

    def set_mirrors(self):
        """
        Set optional server list.
        """
        for i, mirror in enumerate(self.mirrors):
            self.ui.SelectMirror.addItem(_fromUtf8(""))
            self.ui.SelectMirror.setItemText(
                i, _translate("Util", mirror["tag"], None))
            self.set_platform_label()

    def set_label_color(self, label, color):
        """
        Set the :attr:`color` of a :attr:`label`.

        :param label: Label on the main dialog.
        :type: :class:`PyQt4.QtGui.QLabel`
        :param color: Color to be set on the label.
        :type color: str
        """
        if color == "GREEN":
            rgb = "#37b158"
        elif color == "RED":
            rgb = "#e27867"
        elif color == "BLACK":
            rgb = "#b1b1b1"
        else:
            rgb = "#ffffff"
        label.setStyleSheet("QLabel {color: %s}" % rgb)

    def set_label_text(self, label, text):
        """
        Set the :attr:`text` of a :attr:`label`.

        :param label: Label on the main dialog.
        :type: :class:`PyQt4.QtGui.QLabel`
        :param text: Message to be set on the label.
        :type text: unicode
        """
        label.setText(_translate("Util", text, None))

    def set_conn_status(self, status):
        """
        Set the information of connection status to the current server
        selected.
        """
        if status == -1:
            self.set_label_color(self.ui.labelConnStat, "BLACK")
            self.set_label_text(self.ui.labelConnStat, unicode(
                _translate("Util", "Checking...", None)))
        elif status in [0, 1]:
            if status:
                color, stat = "GREEN", unicode(_translate(
                    "Util", "[OK]", None))
            else:
                color, stat = "RED", unicode(_translate(
                    "Util", "[Failed]", None))
            self.set_label_color(self.ui.labelConnStat, color)
            self.set_label_text(self.ui.labelConnStat, stat)

    def set_version(self):
        version = "".join(['v', __version__, ' ', __release__])
        self.set_label_text(self.ui.VersionLabel, version)

    def set_info(self):
        """
        Set the information of the current local data file.
        """
        info = RetrieveData.get_info()
        ver = info["Version"]
        self._cur_ver = ver
        self.set_label_text(self.ui.labelVersionData, ver)
        build = info["Buildtime"]
        build = CommonUtil.timestamp_to_date(build)
        self.set_label_text(self.ui.labelReleaseData, unicode(build))

    def set_down_progress(self, progress, message):
        """
        Set :attr:`progress` position of the progress bar with a
        :attr:`message`.

        :param progress: Progress position to be set on the progress bar.
        :type progress: int
        :param message: Message to be set on the progress bar.
        :type message: str
        """
        self.ui.Prog.setProperty("value", progress)
        self.set_conn_status(1)
        self.ui.Prog.setFormat(message)

    def set_platform_label(self):
        """
        Set the information of the label indicating current operating system
        platform.
        """
        color = "GREEN" if self.plat_flag else "RED"
        self.set_label_color(self.ui.labelOSStat, color)
        self.set_label_text(self.ui.labelOSStat, "[%s]" % self.platform)

    def set_func_list(self, new=0):
        """
        Draw the function list and decide whether to load the default
        selection configuration or not.

        :param new: A flag indicating whether to load the default selection
            configuration or not. Default value is `0`.

            ===  ===================
            new  Operation
            ===  ===================
            0    Use user config.
            1    Use default config.
            ===  ===================
        :type new: int
        """
        self.ui.Functionlist.clear()
        self.ui.FunctionsBox.setTitle(_translate(
            "Util", "Functions", None))
        if new:
            for ip in range(2):
                choice, defaults, slices = RetrieveData.get_choice(ip)
                if os.path.isfile(self.custom):
                    choice.insert(0, [4, 1, 0, "customize"])
                    defaults[0x04] = [1]
                    for i in range(len(slices)):
                        slices[i] += 1
                    slices.insert(0, 0)
                self.choice[ip] = choice
                self.slices[ip] = slices
                funcs = []
                for func in choice:
                    if func[1] in defaults[func[0]]:
                        funcs.append(1)
                    else:
                        funcs.append(0)
                self._funcs[ip] = funcs

    def set_list_item_unchecked(self, item_id):
        """
        Set a specified item to become unchecked in the function list.

        :param item_id: Index number of a specified item in the function list.
        :type: int
        """
        self._funcs[self._ipv_id][item_id] = 0
        item = self.ui.Functionlist.item(item_id)
        item.setCheckState(QtCore.Qt.Unchecked)

    def refresh_func_list(self):
        """
        Refresh the items in the function list by user settings.
        """
        ip_flag = self._ipv_id
        self.ui.Functionlist.clear()

        for f_id, func in enumerate(self.choice[self._ipv_id]):
            item = QtGui.QListWidgetItem()
            if self._funcs[ip_flag][f_id] == 1:
                check = QtCore.Qt.Checked
            else:
                check = QtCore.Qt.Unchecked
            item.setCheckState(check)
            item.setText(_translate("Util", func[3], None))
            self.ui.Functionlist.addItem(item)

    def set_make_progress(self, mod_name, mod_num):
        """
        Start operations to show progress while making hosts file.

        .. note:: This method is the slot responses to the info_trigger signal
            :attr:`mod_name`, :attr:`mod_num` from an instance of
            :class:`~gui._make.QSubMakeHosts` class while making operations
            are proceeding.

        :param mod_name: Tag of a specified hosts module in current progress.
        :type mod_name: str
        :param mod_num: Number of current module in the operation sequence.
        :type mod_num: int

        .. seealso:: :attr:`info_trigger` in
            :class:`~gui._make.QSubMakeHosts` class.
        """
        total_mods_num = self._funcs[self._ipv_id].count(1) + 1
        prog = 100 * mod_num / total_mods_num
        self.ui.Prog.setProperty("value", prog)
        module = unicode(_translate("Util", mod_name, None))
        message = unicode(_translate(
            "Util", "Applying module: %s(%s/%s)", None)
        ) % (module, mod_num, total_mods_num)
        self.ui.Prog.setFormat(message)
        self.set_make_message(message)

    def set_message(self, title, message):
        """
        Show a message box with a :attr:`message` and a :attr:`title`.

        :param title: Title of the message box to be displayed.
        :type title: unicode
        :param message: Message in the message box.
        :type message: unicode
        """
        self.ui.FunctionsBox.setTitle(_translate("Util", title, None))
        self.ui.Functionlist.clear()
        item = QtGui.QListWidgetItem()
        item.setText(message)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.ui.Functionlist.addItem(item)

    def set_make_message(self, message, start=0):
        """
        List message for the current operating progress while making the new
        hosts file in function list.

        :param message: Message to be displayed in the function list.
        :type message: unicode
        :param start: A flag indicating whether the message is the first one
            in the making progress or not. Default value is `0`.

            =====  ==============
            start  Status
            =====  ==============
            0      Not the first.
            1      First.
            =====  ==============
        :type start: int
        """
        if start:
            self.ui.FunctionsBox.setTitle(_translate(
                "Util", "Progress", None))
            self.ui.Functionlist.clear()
        item = QtGui.QListWidgetItem()
        item.setText("- " + message)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.ui.Functionlist.addItem(item)

    def warning_permission(self):
        """
        Show permission error warning message box.
        """
        QtGui.QMessageBox.warning(
            self, _translate("Util", "Warning", None),
            _translate("Util",
                       "You do not have permissions to change the \n"
                       "hosts file.\n"
                       "Please run this program as Administrator/root\n"
                       "so it can modify your hosts file."
                , None))

    def warning_download(self):
        """
        Show download error warning message box.
        """
        QtGui.QMessageBox.warning(
            self, _translate("Util", "Warning", None),
            _translate("Util",
                       "Error retrieving data from the server.\n"
                       "Please try another server.", None))

    def warning_incorrect_datafile(self):
        """
        Show incorrect data file warning message box.
        """
        msg_title = "Warning"
        msg = unicode(_translate("Util",
                                 "Incorrect Data file!\n"
                                 "Please use the \"Download\" key to \n"
                                 "fetch a new data file.", None))
        self.set_message(unicode(msg_title), msg)
        self.ui.ButtonApply.setEnabled(False)
        self.ui.ButtonANSI.setEnabled(False)
        self.ui.ButtonUTF.setEnabled(False)

    def warning_no_datafile(self):
        """
        Show no data file warning message box.
        """
        msg_title = "Warning"
        msg = unicode(_translate("Util",
                                 "Data file not found!\n"
                                 "Please use the \"Download\" key to \n"
                                 "fetch a new data file.", None))
        self.set_message(unicode(msg_title), msg)
        self.ui.ButtonApply.setEnabled(False)
        self.ui.ButtonANSI.setEnabled(False)
        self.ui.ButtonUTF.setEnabled(False)

    def question_apply(self):
        """
        Show confirm question message box before applying hosts file.

        :return: A flag indicating whether user has accepted to continue the
            operations or not.

            ======  =========
            return  Operation
            ======  =========
            True    Continue
            False   Cancel
            ======  =========
        :rtype: bool
        """
        msg_title = unicode(_translate("Util", "Notice", None))
        msg = unicode(_translate("Util",
                                 "Are you sure you want to apply changes \n"
                                 "to the hosts file on your system?\n\n"
                                 "This operation could not be reverted if \n"
                                 "you have not made a backup of your \n"
                                 "current hosts file.", None))
        choice = QtGui.QMessageBox.question(
            self, msg_title, msg,
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
            QtGui.QMessageBox.No
        )
        if choice == QtGui.QMessageBox.Yes:
            return True
        else:
            return False

    def info_uptodate(self):
        """
        Draw data file is up-to-date message box.
        """
        QtGui.QMessageBox.information(
            self, _translate("Util", "Notice", None),
            _translate("Util", "Data file is up-to-date.", None))

    def info_complete(self):
        """
        Draw operation complete message box.
        """
        QtGui.QMessageBox.information(
            self, _translate("Util", "Complete", None),
            _translate("Util", "Operation completed", None))

    def set_make_start_btns(self):
        """
        Set button status while making hosts operations started.
        """
        self.ui.Functionlist.setEnabled(False)
        self.ui.SelectIP.setEnabled(False)
        self.ui.ButtonCheck.setEnabled(False)
        self.ui.ButtonUpdate.setEnabled(False)
        self.ui.ButtonApply.setEnabled(False)
        self.ui.ButtonANSI.setEnabled(False)
        self.ui.ButtonUTF.setEnabled(False)
        self.ui.ButtonExit.setEnabled(False)

    def set_make_finish_btns(self):
        """
        Set button status while making hosts operations finished.
        """
        self.ui.Functionlist.setEnabled(True)
        self.ui.SelectIP.setEnabled(True)
        self.ui.ButtonCheck.setEnabled(True)
        self.ui.ButtonUpdate.setEnabled(True)
        self.ui.ButtonApply.setEnabled(False)
        self.ui.ButtonANSI.setEnabled(False)
        self.ui.ButtonUTF.setEnabled(False)
        self.ui.ButtonExit.setEnabled(True)

    def set_update_click_btns(self):
        """
        Set button status while `CheckUpdate` button clicked.
        """
        self.ui.ButtonApply.setEnabled(True)
        self.ui.ButtonANSI.setEnabled(True)
        self.ui.ButtonUTF.setEnabled(True)

    def set_update_start_btns(self):
        """
        Set button status while operations to check update of hosts data file
        started.
        """
        self.ui.SelectMirror.setEnabled(False)
        self.ui.ButtonCheck.setEnabled(False)
        self.ui.ButtonUpdate.setEnabled(False)

    def set_update_finish_btns(self):
        """
        Set button status while operations to check update of hosts data file
        finished.
        """
        self.ui.SelectMirror.setEnabled(True)
        self.ui.ButtonCheck.setEnabled(True)
        self.ui.ButtonUpdate.setEnabled(True)

    def set_fetch_click_btns(self):
        """
        Set button status while `FetchUpdate` button clicked.
        """
        self.ui.Functionlist.setEnabled(False)
        self.ui.ButtonApply.setEnabled(False)
        self.ui.ButtonANSI.setEnabled(False)
        self.ui.ButtonUTF.setEnabled(False)

    def set_fetch_start_btns(self):
        """
        Set button status while operations to retrieve hosts data file
        started.
        """
        self.ui.SelectMirror.setEnabled(False)
        self.ui.ButtonCheck.setEnabled(False)
        self.ui.ButtonUpdate.setEnabled(False)
        self.ui.ButtonApply.setEnabled(False)
        self.ui.ButtonANSI.setEnabled(False)
        self.ui.ButtonUTF.setEnabled(False)
        self.ui.ButtonExit.setEnabled(False)

    def set_fetch_finish_btns(self, error=0):
        """
        Set button status while operations to retrieve hosts data file
        finished.

        :param error: A flag indicating if error occurs while retrieving hosts
            data file from the server.
        :type error: int
        """
        if error:
            self.ui.ButtonApply.setEnabled(False)
            self.ui.ButtonANSI.setEnabled(False)
            self.ui.ButtonUTF.setEnabled(False)
        else:
            self.ui.ButtonApply.setEnabled(True)
            self.ui.ButtonANSI.setEnabled(True)
            self.ui.ButtonUTF.setEnabled(True)
        self.ui.Functionlist.setEnabled(True)
        self.ui.SelectMirror.setEnabled(True)
        self.ui.ButtonCheck.setEnabled(True)
        self.ui.ButtonUpdate.setEnabled(True)
        self.ui.ButtonExit.setEnabled(True)
