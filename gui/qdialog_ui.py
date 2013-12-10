#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  qdialog_ui.py :
#
# Copyleft (C) 2014 - huhamhire hosts team <develop@huhamhire.com>
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

from language import LangUtil
from util_ui import Ui_Util, _translate, _fromUtf8

import sys
sys.path.append("..")
from util import RetrieveData, CommonUtil

# Path to store language files
LANG_DIR = "./gui/lang/"


class QDialogUI(QtGui.QDialog, object):
    """
    Attributes:
        _cur_ver (str): A string indicating the current version of hosts data
            file.
        _trans (obj): A QtCore.QTranslator object indicating the current UI
            language setting.
        platform (str): A string indicating the platform of current operating
            system. The value could be "Windows", "Linux", "Unix", "OS X", and
            of course "Unkown".
        plat_flag (bool): A boolean flag indicating whether the current os is
            supported or not.
        Ui (str): A user interface object indicating the main dialog of this
            program.
    """
    _cur_ver = ""
    _trans = None

    # OS related configuration
    platform = ''
    plat_flag = True
    Ui = None

    def __init__(self):
        """Initialize a new instance of this class - Private Method

        Set the UI object and current translator of the main dialog.
        """
        super(QDialogUI, self).__init__()
        self.Ui = Ui_Util()
        self.Ui.setupUi(self)
        self.set_style()
        self.set_stylesheet()
        # Set default UI language
        trans = QtCore.QTranslator()
        trans.load(LANG_DIR + "en_US")
        self._trans = trans
        QtGui.QApplication.installTranslator(trans)
        self.set_languages()

    def set_stylesheet(self):
        """Set Stylesheet for main frame - Public Method

        Define the style sheet of main dialog.
        """
        app = QtGui.QApplication.instance()
        with open("./gui/theme/default.qss", "r") as qss:
            app.setStyleSheet(qss.read())

    def set_style(self):
        """Set window style - Public Method

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
        """Set items in SelectLang widget - Public Method

        Set optional language selection items in the SelectLang widget.
        """
        self.Ui.SelectLang.clear()
        langs = LangUtil.language
        langs_not_found = []
        for locale in langs:
            if not os.path.isfile(LANG_DIR + locale + ".qm"):
                langs_not_found.append(locale)
        for locale in langs_not_found:
            langs.pop(locale)
        LangUtil.language = langs
        if len(langs) <= 1:
            self.Ui.SelectLang.setEnabled(False)
        # Block the signal while set the language selecions.
        self.Ui.SelectLang.blockSignals(True)
        sys_locale = LangUtil.get_locale()
        if sys_locale not in langs.keys():
            sys_locale = "en_US"
        for i, locale in enumerate(sorted(langs.keys())):
            if sys_locale == locale:
                select = i
            lang = langs[locale]
            self.Ui.SelectLang.addItem(_fromUtf8(""))
            self.Ui.SelectLang.setItemText(i, lang)
        self.Ui.SelectLang.blockSignals(False)
        self.Ui.SelectLang.setCurrentIndex(select)

    def set_label_color(self, label, color):
        """Set the color of a label - Public Method

        Set a specified label ({label}) to show with specified color
        ({color}).

        Args:
            label (obj): An instance of PyQt4.QtGui.QLabel class on the main
                dialog.
            color (str): A string indicating the color to be shown on the
                lable.
        """
        if color == "GREEN":
            rgb = "#37b158"
        elif color == "RED":
            rgb = "#e27867"
        elif color == "BLACK":
            rgb = "#b1b1b1"
        label.setStyleSheet("QLabel {color: %s}" % rgb)

    def set_label_text(self, label, text):
        """Set the text of a label - Public Method

        Set a specified label ({label}) to show specified text ({text}).

        Args:
            label (obj): An instance of PyQt4.QtGui.QLabel class on the main
                dialog.
            text (str): A string indicating the message to be shown on the
                lable.
        """
        label.setText(_translate("Util", text, None))

    def set_conn_status(self, status):
        """Set connection status info - Public Method

        Set the information of connection status to the current server
        selected.
        """
        if status == -1:
            self.set_label_color(self.Ui.labelConnStat, "BLACK")
            self.set_label_text(self.Ui.labelConnStat, unicode(
                _translate("Util", "Checking...", None)))
        elif status in [0, 1]:
            if status:
                color, stat = "GREEN", unicode(_translate(
                    "Util", "[OK]", None))
            else:
                color, stat = "RED", unicode(_translate(
                    "Util", "[Failed]", None))
            self.set_label_color(self.Ui.labelConnStat, color)
            self.set_label_text(self.Ui.labelConnStat, stat)

    def set_info(self):
        """Set data file info - Public Method

        Set the information of the current local data file.
        """
        info = RetrieveData.get_info()
        ver = info["Version"]
        self._cur_ver = ver
        self.set_label_text(self.Ui.labelVersionData, ver)
        build = info["Buildtime"]
        build = CommonUtil.timestamp_to_date(build)
        self.set_label_text(self.Ui.labelReleaseData, build)

    def set_down_progress(self, prog, msg):
        """Set progress bar - Public Method

        Set the progress bar to a specified progress position ({prog}) with a
        specified message ({msg}).

        Args:
            prog (int): An integer indicating the progress to be set on the
                progress bar.
            msg (str): A string indicating the message to be shown on the
                progress bar.
        """
        self.Ui.Prog.setProperty("value", prog)
        self.set_conn_status(1)
        self.Ui.Prog.setFormat(msg)

    def set_platform_label(self):
        """Set label of OS info - Public Method

        Set the information of the label indicating current operating system
        platform.
        """
        color = "GREEN" if self.plat_flag else "RED"
        self.set_label_color(self.Ui.labelOSStat, color)
        self.set_label_text(self.Ui.labelOSStat, "[%s]" % self.platform)

    def set_func_list(self, new=0):
        """Set the function list - Public Method

        Draw the function list and decide whether to load the default
        selection configuration or not.

        Arg:
            new (int): A flag integer indicating whether to load the default
                selection configuration or not. 0 -> user user config,
                1 -> use default config. Default by 0.
        """
        ip_flag = self._ipv_id
        self.Ui.Functionlist.clear()
        self.Ui.FunctionsBox.setTitle(_translate(
            "Util", "Functions", None))
        if new:
            for ip in range(2):
                choice, defaults, slices = RetrieveData.get_choice(ip)
                self.choice[ip] = choice
                self.slices[ip] = slices
                funcs = []
                for func in choice:
                    item = QtGui.QListWidgetItem()
                    if func[1] in defaults[func[0]]:
                        funcs.append(1)
                    else:
                        funcs.append(0)
                self._funcs[ip] = funcs

    def set_list_item_unchecked(self, item_id):
        """Set list item to be unchecked - Public Method

        Set a specified item ({item_id}) to become unchecked in the function
        list.

        Arg:
            item_id (int): An integer indicating the id number of a specified
                item in the function list.
        """
        self._funcs[self._ipv_id][item_id] = 0
        item = self.Ui.Functionlist.item(item_id)
        item.setCheckState(QtCore.Qt.Unchecked)

    def refresh_func_list(self):
        """Refresh the function list - Public Method

        Refresh the items in the function list by user settings.
        """
        ip_flag = self._ipv_id
        self.Ui.Functionlist.clear()
        for f_id, func in enumerate(self.choice[self._ipv_id]):
            item = QtGui.QListWidgetItem()
            if self._funcs[ip_flag][f_id] == 1:
                check = QtCore.Qt.Checked
            else:
                check = QtCore.Qt.Unchecked
            item.setCheckState(check)
            item.setText(_translate("Util", func[3], None))
            self.Ui.Functionlist.addItem(item)

    def set_make_progress(self, mod_name, mod_num):
        """Operations to show progress while making hosts file - Public Method

        The slot response to the info_trigger signal ({mod_name}, {mod_num})
        from an instance of QSubMakeHosts class while making operations are
        proceeded.

        Args:
            mod_name (str): A string indicating the name of a specified hosts
                module in current progress.
            mod_num (int): An integer indicating the number of current module
                in the operation sequence.
        """
        total_mods_num = self._funcs[self._ipv_id].count(1) + 1
        prog = 100 * mod_num / total_mods_num
        self.Ui.Prog.setProperty("value", prog)
        format = unicode(_translate(
            "Util", "Applying module: %s(%s/%s)", None)) % (
            mod_name, mod_num, total_mods_num)
        self.Ui.Prog.setFormat(format)
        self.set_make_message(format)


    def set_message(self, title, msg):
        """Set a message box - Public Method

        Show a message box with a specified message ({msg}) with a specified
        title ({title}).

        Args:
            title (str): A string indicating the title of the message box.
            msg (str): A string indicating the message to be shown in the
                message box.
        """
        self.Ui.FunctionsBox.setTitle(_translate("Util", title, None))
        self.Ui.Functionlist.clear()
        item = QtGui.QListWidgetItem()
        item.setText(msg)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.Ui.Functionlist.addItem(item)

    def set_make_message(self, msg, start=0):
        """Operations to show making progress in function list - Public Method

        List message for the current operating progress while making the new
        hosts file.

        Args:
            msg (str): A string indicating the message to show in the function
                list.
            start (int): A flag integer indicating whether the message is the
                first of the making progress or not. 1: first, 0: not the
                first. Default by 0.
        """
        if start:
            self.Ui.FunctionsBox.setTitle(_translate(
                "Util", "Progress", None))
            self.Ui.Functionlist.clear()
        item = QtGui.QListWidgetItem()
        item.setText("- " + msg)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.Ui.Functionlist.addItem(item)

    def warning_permission(self):
        """Show permission error warning - Public Method

        Draw permission error warning message box.
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
        """Show download error warning - Public Method

        Draw download error warning message box.
        """
        QtGui.QMessageBox.warning(
            self, _translate("Util", "Warning", None),
            _translate("Util",
                "Error retrieving data from the server.\n"
                "Please try another server.", None))

    def warning_incorrect_datafile(self):
        """Show incorrect data file warning - Public Method

        Draw incorrect data file warning message box.
        """
        msg_title = "Warning"
        msg = unicode(_translate("Util",
            "Incorrect Data file!\n"
            "Please use the \"Download\" key to \n"
            "fetch a new data file.", None))
        self.set_message(msg_title, msg)
        self.Ui.ButtonApply.setEnabled(False)
        self.Ui.ButtonANSI.setEnabled(False)
        self.Ui.ButtonUTF.setEnabled(False)

    def warning_no_datafile(self):
        """Show no data file warning - Public Method

        Draw no data file warning message box.
        """
        msg_title = "Warning"
        msg = unicode(_translate("Util",
            "Data file not found!\n"
            "Please use the \"Download\" key to \n"
            "fetch a new data file.", None))
        self.set_message(msg_title, msg)
        self.Ui.ButtonApply.setEnabled(False)
        self.Ui.ButtonANSI.setEnabled(False)
        self.Ui.ButtonUTF.setEnabled(False)

    def question_apply(self):
        """Show confirm make question - Public Method

        Draw confirm make question message box.

        Returns:
            A bool flag indicating whether user has accepted to continue the
            operations or not. True: Continue, False: Cancel.
        """
        msg_title = unicode(_translate("Util", "Notice", None))
        msg = unicode(_translate("Util",
            "Are you sure you want to apply changes \n"
            "to the hosts file on your system?\n\n"
            "This operation could not be reverted if \n"
            "you have not made a backup of your \n"
            "current hosts file.", None))
        choice = QtGui.QMessageBox.question(self, msg_title, msg,
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
            QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            return True
        else:
            return False

    def info_uptodate(self):
        """Show up-to-date message - Public Method

        Draw data file is up-to-date message box.
        """
        QtGui.QMessageBox.information(
            self, _translate("Util", "Notice", None),
            _translate("Util", "Data file is up-to-date.", None))

    def info_complete(self):
        """Show complete message - Public Method

        Draw operation complete message box.
        """
        QtGui.QMessageBox.information(
            self, _translate("Util", "Complete", None),
            _translate("Util", "Operation completed", None))



    def set_make_start_btns(self):
        self.Ui.Functionlist.setEnabled(False)
        self.Ui.SelectIP.setEnabled(False)
        self.Ui.ButtonCheck.setEnabled(False)
        self.Ui.ButtonUpdate.setEnabled(False)
        self.Ui.ButtonApply.setEnabled(False)
        self.Ui.ButtonANSI.setEnabled(False)
        self.Ui.ButtonUTF.setEnabled(False)
        self.Ui.ButtonExit.setEnabled(False)

    def set_make_finish_btns(self):
        self.Ui.Functionlist.setEnabled(True)
        self.Ui.SelectIP.setEnabled(True)
        self.Ui.ButtonCheck.setEnabled(True)
        self.Ui.ButtonUpdate.setEnabled(True)
        self.Ui.ButtonApply.setEnabled(False)
        self.Ui.ButtonANSI.setEnabled(False)
        self.Ui.ButtonUTF.setEnabled(False)
        self.Ui.ButtonExit.setEnabled(True)

    def set_update_click_btns(self):
        self.Ui.ButtonApply.setEnabled(True)
        self.Ui.ButtonANSI.setEnabled(True)
        self.Ui.ButtonUTF.setEnabled(True)

    def set_update_start_btns(self):
        self.Ui.SelectMirror.setEnabled(False)
        self.Ui.ButtonCheck.setEnabled(False)
        self.Ui.ButtonUpdate.setEnabled(False)

    def set_update_finish_btns(self):
        self.Ui.SelectMirror.setEnabled(True)
        self.Ui.ButtonCheck.setEnabled(True)
        self.Ui.ButtonUpdate.setEnabled(True)

    def set_fetch_click_btns(self):
        self.Ui.Functionlist.setEnabled(False)
        self.Ui.ButtonApply.setEnabled(False)
        self.Ui.ButtonANSI.setEnabled(False)
        self.Ui.ButtonUTF.setEnabled(False)

    def set_fetch_start_btns(self):
        self.Ui.SelectMirror.setEnabled(False)
        self.Ui.ButtonCheck.setEnabled(False)
        self.Ui.ButtonUpdate.setEnabled(False)
        self.Ui.ButtonApply.setEnabled(False)
        self.Ui.ButtonANSI.setEnabled(False)
        self.Ui.ButtonUTF.setEnabled(False)
        self.Ui.ButtonExit.setEnabled(False)

    def set_fetch_finish_btns(self, error=0):
        if error:
            self.Ui.ButtonApply.setEnabled(False)
            self.Ui.ButtonANSI.setEnabled(False)
            self.Ui.ButtonUTF.setEnabled(False)
        else:
            self.Ui.ButtonApply.setEnabled(True)
            self.Ui.ButtonANSI.setEnabled(True)
            self.Ui.ButtonUTF.setEnabled(True)
        self.Ui.Functionlist.setEnabled(True)
        self.Ui.SelectMirror.setEnabled(True)
        self.Ui.ButtonCheck.setEnabled(True)
        self.Ui.ButtonUpdate.setEnabled(True)
        self.Ui.ButtonExit.setEnabled(True)
