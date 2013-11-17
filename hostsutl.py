#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hostsutl.py : Main parts of Hosts Setup Utility
#
# Copyleft (C) 2013 - huhamhire hosts team <develop@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING
# THE WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE.
# =====================================================================

__version__ = "1.9.6"
__revision__ = "$Id$"
__author__ = "huhamhire <me@huhamhire.com>"

__all__ = [
    "LANG_DIR", "MainDialog", "QSubChkConnection", "QSubFetchUpdate",
    "QSubMakeHosts", "QSubChkUpdate",]

import json
import os
import shutil
import socket
import sys
import time
import urllib

from PyQt4 import QtCore, QtGui
from zipfile import BadZipfile

from qthostsui import Ui_HostsUtlMain, _fromUtf8, _encoding, _translate
from retrievedata import RetrieveData, make_hosts
from utilities import Utilities, LangUtilities

# Path to store language files
LANG_DIR = "./lang/"

class MainDialog(QtGui.QDialog):
    """A class to manage the operations and UI of Hosts Setup Utility

    MainDialog class is a subclasse of PyQt4.QtGui.QDialog which is used to
    make the main dialog of this hosts setup utility.
    This class contains a set of tools used to manage the operations while
    modifying the hosts file of current operating system. Including methods
    to manage operations to update data file, download data file, configure
    hosts, make hosts file, backup hosts file, and restore backup.
    The MainDialog class also provides QT slots to deal with the QT singles
    emitted by the widgets on the main dialog operated by users. Extend
    methods dealing with the user interface is also given by this class.

    Attributes:
        _cur_ver (str): A string indicating the current version of hosts data
            file.
        _ipv_id (int): An integer indicating current IP version setting. The
            value could be 1 or 0. 1 represents IPv6 while 1 represents IPv4.
        _is_root (int): An integer indicating whether the program is run with
            admin/root privileges. The value could be 1 or 0.
        _down_flag (int) An integer indicating the downloading status of
            current session. 1 represents data file is being downloaded.
        _funcs (list): A list containing two lists with the information of
            function list for IPv4 and IPv6 environment.
        _make_cfg (dict): A dictionary containing the selection control bytes
            to make a hosts file.
        _make_mode (str): A string indicating the operation mode for making
            hosts file.
        _make_path (str): A string indicating the path to store the hosts file
            in export mode.
        _sys_eol (str): A string indicating the End-Of-Line marker.
        _update (dict): A dictionary containing the update information of the
            current data file on server.
        _trans (obj): A QtCore.QTranslator object indicating the current UI
            language setting.
        choice (list): A list containing two lists with the selection of
            functions for IPv4 and IPv6 environment.
        slices (list): A list containing two lists with integers indicating
            the number of function items from different parts listed in the
            function list.
        initd (int): An integer indicating how many times has the main dialog
            been initialized. This value would be referenced for translator
            to set the language of the main dialog.
        platform (str): A string indicating the platform of current operating
            system. The value could be "Windows", "Linux", "Unix", "OS X", and
            of course "Unkown".
        hostname (str): A string indicating the hostname of current operating
            system. This attribute would be used for linux clients.
        hostspath (str): A string indicating the absolute path of the hosts
            file on current operating system.
        Ui (str): A user interface object indicating the main dialog of this
            program.
        _mirr_id (int): An integer indicating current index number of mirrors.
        mirrors (list): A dictionary containing tag, test url, and update url
            of mirrors.
        __list_trans (list): A list containing names of function list items
            for translator to translate.
        filename (str): A string indicating the filename of the data file
            containing data to make a hosts file.
        infofile (str): A string indicating the filename of the info file
            containing metadata of the data file in JSON format.
    """
    _cur_ver = ""
    _ipv_id = 0
    _is_root = 0
    _down_flag = 0
    _funcs = [[], []]
    _make_cfg = {}
    _make_mode = ""
    _make_path = "./hosts"
    _sys_eol = ""
    _update = {}
    _trans = None

    choice = [[], []]
    slices = [[], []]

    initd = 0

    Ui = None
    # OS related configuration
    platform = ''
    hostname = ''
    hostspath = ''
    # Mirror related configuration
    _mirr_id = 0
    mirrors = []
    # Name of items from the function list to be localized
    __list_trans = [
        _translate("HostsUtlMain", "google(cn)", None),
        _translate("HostsUtlMain", "google(us)", None),
        _translate("HostsUtlMain", "activation-helper", None),
        _translate("HostsUtlMain", "others", None),
        _translate("HostsUtlMain", "adblock-hostsx", None),
        _translate("HostsUtlMain", "adblock-mvps", None),
        _translate("HostsUtlMain", "adblock-mwsl", None),
        _translate("HostsUtlMain", "adblock-yoyo", None), ]
    # Data file related configuration
    filename = "hostslist.data"
    infofile = "hostsinfo.json"

    def __init__(self, Ui, trans):
        """Initialize a new instance of this class - Private Method

        Set the UI object and current translator of the main dialog.

        Args:
            Ui (obj): A user interface object indicating the main dialog of
                this program.
            trans (obj): A PyQt4.QtCore.QTranslator object indicating the
                current UI language setting.
        """
        super(MainDialog, self).__init__()
        self.Ui = Ui
        self._trans = trans

    def on_Mirror_changed(self, mirr_id):
        """Change the current mirror setting - Public Method

        The slot response to the signal ({mirr_id}) from SelectMirror widget
        while the value is changed.

        Args:
            mirr_id (int): An integer indicating current index number of
                mirrors.
        """
        self._mirr_id = mirr_id
        self.check_connection()

    def on_IPVersion_changed(self, ipv_id):
        """Change the current IP version setting - Public Method

        The slot response to the signal ({ipv_id}) from SelectIP widget while
        the value is changed.

        Args:
            ipv_id (int): An integer indicating current IP version setting.
                The value could be 1 or 0. 1 represents IPv6 while 1
                represents IPv4.
        """
        if self._ipv_id != ipv_id:
            self._ipv_id = ipv_id
            self.set_func_list(0)
            self.refresh_func_list()

    def on_Selection_changed(self, item):
        """Change the function selection setting - Public Method

        The slot response to the signal ({item}) from Functionlist widget
        while the selection of the items is changed. This method would change
        the current selection of functions.

        Args:
            item (int): An integer indicating the row number of the item
                listed in Functionlist which is changed by user.
        """
        ip_flag = self._ipv_id
        func_id = item.listWidget().row(item)
        if self._funcs[ip_flag][func_id] == 0:
            self._funcs[ip_flag][func_id] = 1
        else:
            self._funcs[ip_flag][func_id] = 0
        mutex = RetrieveData.get_ids(self.choice[ip_flag][func_id][2])
        for c_id, c in enumerate(self.choice[ip_flag]):
            if c[0] == self.choice[ip_flag][func_id][0]:
                if c[1] in mutex and self._funcs[ip_flag][c_id] == 1:
                    self._funcs[ip_flag][c_id] = 0
                    item = self.Ui.Functionlist.item(c_id)
        self.refresh_func_list()

    def on_Lang_changed(self, lang):
        """Change the UI language setting - Public Method

        The slot response to the signal ({lang}) from SelectLang widget while
        the value is changed. This method would change the language of the UI.

        Args:
            lang (str): A string indicating the language which is selected by
                user.
                This string uses the for of IETF language tag. For example:
                en_US, en_GB, etc.
        """
        new_lang = LangUtilities.get_locale_by_language(unicode(lang))
        trans = QtCore.QTranslator()
        global LANG_DIR
        trans.load(LANG_DIR + new_lang)
        QtGui.QApplication.removeTranslator(self._trans)
        QtGui.QApplication.installTranslator(trans)
        self._trans = trans
        self.Ui.retranslateUi(self)
        self.init_main()
        self.check_connection()

    def on_MakeHosts_clicked(self):
        """Start making hosts file - Public Method

        The slot response to the signal from ButtonApply widget while the
        button is clicked. This method would call operations to make a hosts
        file.
        No operations would be called if current session does not have the
        privileges to change the hosts file.
        """
        if not self._is_root:
            self.warning_permission()
            return
        if self.question_apply():
            self._make_path = "./hosts"
            self.make_hosts("system")
        else:
            return

    def on_MakeANSI_clicked(self):
        """Export hosts ANSI - Public Method

        The slot response to the signal from ButtonANSI widget while the
        button is clicked. This method would call operations to export a hosts
        file encoding in ANSI.
        """
        self._make_path = self.export_hosts()
        if unicode(self._make_path) != u'':
            self.make_hosts("ansi")

    def on_MakeUTF8_clicked(self):
        """Export hosts in UTF-8 - Public Method

        The slot response to the signal from ButtonUTF widget while the
        button is clicked. This method would call operations to export a hosts
        file encoding in UTF-8.
        """
        self._make_path = self.export_hosts()
        if unicode(self._make_path) != u'':
            self.make_hosts("utf-8")

    def on_Backup_clicked(self):
        """Backup system hosts file - Public Method

        The slot response to the signal from ButtonBackup widget while the
        button is clicked. This method would call operations to backup the
        hosts file of current operating system.
        """
        l_time = time.localtime(time.time())
        backtime = time.strftime("%Y-%m-%d-%H%M%S", l_time)
        filename = "hosts_" + backtime + ".bak"
        if self.platform == "OS X":
            filename = "/Users/" + filename
        filepath = QtGui.QFileDialog.getSaveFileName(
            self, _translate("HostsUtlMain", "Backup hosts", None),
            QtCore.QString(filename),
            _translate("HostsUtlMain", "Backup File(*.bak)", None))
        if unicode(filepath) != u'':
            shutil.copy2(self.hostspath, unicode(filepath))
            self.info_complete()

    def on_Restore_clicked(self):
        """Restore hosts file - Public Method

        The slot response to the signal from ButtonRestore widget while the
        button is clicked. This method would call operations to restore a
        previously backed up hosts file.
        No operations would be called if current session does not have the
        privileges to change the hosts file.
        """
        if not self._is_root:
            self.warning_permission()
            return
        filename = ''
        if self.platform == "OS X":
            filename = "/Users/" + filename
        filepath = QtGui.QFileDialog.getOpenFileName(
            self, _translate("HostsUtlMain", "Restore hosts", None),
            QtCore.QString(filename),
            _translate("HostsUtlMain", "Backup File(*.bak)", None))
        if unicode(filepath) != u'':
            shutil.copy2(unicode(filepath), self.hostspath)
            self.info_complete()

    def on_CheckUpdate_clicked(self):
        """Check data file update - Public Method

        The slot response to the signal from ButtonCheck widget while the
        button is clicked. This method would call operations to fetch update
        information of the latest data file.
        """
        if self.choice != [[], []]:
            self.refresh_func_list()
            self.Ui.ButtonApply.setEnabled(True)
            self.Ui.ButtonANSI.setEnabled(True)
            self.Ui.ButtonUTF.setEnabled(True)
        if self._update == {} or self._update["version"] == \
            unicode(_translate("HostsUtlMain", "[Error]", None)):
            self.check_update()

    def on_FetchUpdate_clicked(self):
        """Fetch data file update - Public Method

        The slot response to the signal from ButtonUpdate widget while the
        button is clicked. This method would call operations to fetch the
        latest data file.
        If no update information has been got from the server, the method to
        check the update would be called.
        If the current data is up-to-date, no data file would be retrieved.
        """
        self._down_flag = 1
        self.Ui.Functionlist.setEnabled(False)
        self.Ui.ButtonApply.setEnabled(False)
        self.Ui.ButtonANSI.setEnabled(False)
        self.Ui.ButtonUTF.setEnabled(False)
        if self._update == {} or self._update["version"] == \
            unicode(_translate("HostsUtlMain", "[Error]", None)):
            self.check_update()
        elif self.new_version():
            self.fetch_update()
        else:
            self.info_uptodate()
            self.finish_fetch()

    def init_main(self):
        """Initialize the main dialog - Public Method

        Set up the elements on the main dialog. Check the environment of
        current operating system and current session.
        """
        self.Ui.SelectMirror.clear()
        # Set mirrors
        self.mirrors = Utilities.set_network("network.conf")
        for i, mirror in enumerate(self.mirrors):
            self.Ui.SelectMirror.addItem(_fromUtf8(""))
            self.Ui.SelectMirror.setItemText(
                i, _translate("HostsUtlMain", mirror["tag"], None))
        self.set_platform()
        self.set_font()
        # Read data file and set function list
        try:
            RetrieveData.unpack()
            RetrieveData.connect_db()
            self.set_func_list(1)
            self.refresh_func_list()
            self.set_info()
        except IOError:
            self.warning_no_datafile()
        except BadZipfile:
            self.warning_incorrect_datafile()
        # Check if current session have root privileges
        self.check_root()
        self.initd += 1

    def reject(self):
        """Response to the reject signal - Public Method

        The slot response to the reject signal from an instance of the main
        dialog. Close this program while the reject signal is emitted.
        """
        self.close()
        return QtGui.QDialog.reject(self)

    def close(self):
        """Response to the close signal - Public Method

        The slot response to the close signal from an instance of the main
        dialog. Close this program while the reject signal is emitted.
        """
        try:
            RetrieveData.clear()
        except:
            pass
        super(MainDialog, self).close()

    def check_root(self):
        """Check root privileges - Public Method

        Check if current session is ran with root privileges.
        """
        is_root = Utilities.check_privileges()[1]
        self._is_root = is_root
        if not is_root:
            self.warning_permission()

    def check_connection(self):
        """Operations to check connection - Public Method

        Call operations to check the connection to current server.
        """
        thread = QSubChkConnection(self)
        thread.trigger.connect(self.set_conn_status)
        thread.start()

    def check_update(self):
        """Operations to check data file update - Public Method

        Call operations to retrieve the metadata of the latest data file from
        a server.
        """
        self.Ui.SelectMirror.setEnabled(False)
        self.Ui.ButtonCheck.setEnabled(False)
        self.Ui.ButtonUpdate.setEnabled(False)
        self.set_label_text(self.Ui.labelLatestData, unicode(
            _translate("HostsUtlMain", "Checking...", None)))
        thread = QSubChkUpdate(self)
        thread.trigger.connect(self.finish_update)
        thread.start()

    def fetch_update(self):
        """Operations to fetch new data file - Public Method

        Call operations to retrieve a new hosts data file from a server.
        """
        self.Ui.SelectMirror.setEnabled(False)
        self.Ui.ButtonCheck.setEnabled(False)
        self.Ui.ButtonUpdate.setEnabled(False)
        self.Ui.ButtonApply.setEnabled(False)
        self.Ui.ButtonANSI.setEnabled(False)
        self.Ui.ButtonUTF.setEnabled(False)
        self.Ui.ButtonExit.setEnabled(False)
        thread = QSubFetchUpdate(self)
        thread.prog_trigger.connect(self.set_downprogbar)
        thread.finish_trigger.connect(self.finish_fetch)
        thread.start()

    def fetch_update_aftercheck(self):
        """Check to fetch data file after check for update - Public Method

        Decide whether to retrieve a new data file from server or not after
        checking update information from a mirror.
        """
        if self._update["version"] == \
            unicode(_translate("HostsUtlMain", "[Error]", None)):
            self.finish_fetch(error=1)
        elif self.new_version():
            self.fetch_update()
        else:
            self.info_uptodate()
            self.finish_fetch()

    def export_hosts(self):
        """Draw export hosts dialog - Public Method

        Show the export dialog and get the path to save the exported hosts
        file.

        Returns:
            A string indicating the path to export a hosts file
        """
        filename = "hosts"
        if self.platform == "OS X":
            filename = "/Users/" + filename
        filepath = QtGui.QFileDialog.getSaveFileName(
            self, _translate("HostsUtlMain", "Export hosts", None),
            QtCore.QString(filename),
            _translate("HostsUtlMain", "hosts File", None))
        return filepath

    def make_hosts(self, mode="system"):
        """Operations to make hosts file - Public Method

        Call operations to make a new hosts file for current system.

        Args:
            mode (str): A string indicating the operation mode for making
                hosts file.
        """
        self.Ui.Functionlist.setEnabled(False)
        self.Ui.SelectIP.setEnabled(False)
        self.Ui.ButtonCheck.setEnabled(False)
        self.Ui.ButtonUpdate.setEnabled(False)
        self.Ui.ButtonApply.setEnabled(False)
        self.Ui.ButtonANSI.setEnabled(False)
        self.Ui.ButtonUTF.setEnabled(False)
        self.Ui.ButtonExit.setEnabled(False)
        self.set_makemsg(unicode(_translate(
            "HostsUtlMain", "Building hosts file...", None)), 1)
        # Avoid conflict while making hosts file
        RetrieveData.disconnect_db()
        self._make_mode = mode
        self.set_cfgbytes(mode)
        thread = QSubMakeHosts(self)
        thread.info_trigger.connect(self.set_makeprog)
        thread.fina_trigger.connect(self.set_makefina)
        thread.move_trigger.connect(self.move_hosts)
        thread.start()

    def move_hosts(self):
        """Move hosts file to the system path after making - Public Method

        The slot response to the move_trigger signal from an instance of
        QSubMakeHosts class while making operations are finished.
        """
        filepath = "hosts"
        msg = unicode(_translate("HostsUtlMain",
            "Copying new hosts file to\n"
            "  %s", None)) % self.hostspath
        self.set_makemsg(msg)
        shutil.copy2(filepath, self.hostspath)
        msg = unicode(_translate("HostsUtlMain",
            "Remove temporary file", None))
        self.set_makemsg(msg)
        os.remove(filepath)
        msg = unicode(_translate("HostsUtlMain",
            "Operation completed", None))
        self.set_makemsg(msg)
        self.info_complete()

    def set_languages(self):
        """Set items in SelectLang widget - Public Method

        Set optional language selection items in the SelectLang widget.
        """
        self.Ui.SelectLang.clear()
        langs = LangUtilities.language
        langs_not_found = []
        for locale in langs:
            if not os.path.isfile(LANG_DIR + locale + ".qm"):
                langs_not_found.append(locale)
        for locale in langs_not_found:
            langs.pop(locale)
        LangUtilities.language = langs
        if len(langs) <= 1:
            self.Ui.SelectLang.setEnabled(False)
        # Block the signal while set the language selecions.
        self.Ui.SelectLang.blockSignals(True)
        sys_locale = LangUtilities.get_locale()
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

    def set_platform(self):
        """Set OS info - Public Method

        Set the information of current operating system platform.
        """
        system, hostname, path, encode, flag = Utilities.check_platform()
        color = "GREEN" if flag else "RED"
        self.set_label_color(self.Ui.labelOSStat, color)
        self.set_label_text(self.Ui.labelOSStat, "[%s]" % system)
        self.platform = system
        self.hostname = hostname
        self.hostspath = path
        if encode == "win_ansi":
            self._sys_eol = "\r\n"
        else:
            self._sys_eol = "\n"

    def set_font(self):
        """Set font and window style - Public Method

        Set the font of the elements on the main dialog with a windows style
        depending on this program.
        """
        system = self.platform
        if system == "Windows":
            font = QtGui.QFont()
            font.setFamily(_fromUtf8("Courier"))
            self.setFont(font)
        elif system == "Linux":
            font = QtGui.QFont()
            font.setFamily(_fromUtf8("Sans"))
            self.setFont(font)
            # Set window style for sudo users.
            QtGui.QApplication.setStyle(
                QtGui.QStyleFactory.create("Cleanlooks"))
        elif system == "OS X":
            pass

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
            rgb = [0, 170, 0]
        elif color == "RED":
            rgb = [255, 0, 0]
        elif color == "BLACK":
            rgb = [0, 0, 0]
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(*rgb))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(*rgb))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(
            QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        label.setPalette(palette)

    def set_label_text(self, label, text):
        """Set the text of a label - Public Method

        Set a specified label ({label}) to show specified text ({text}).

        Args:
            label (obj): An instance of PyQt4.QtGui.QLabel class on the main
                dialog.
            text (str): A string indicating the message to be shown on the
                lable.
        """
        label.setText(_translate("HostsUtlMain", text, None))

    def set_conn_status(self, status):
        """Set connection status info - Public Method

        Set the information of connection status to the current server
        selected.
        """
        if status == -1:
            self.set_label_color(self.Ui.labelConnStat, "BLACK")
            self.set_label_text(self.Ui.labelConnStat, unicode(
                _translate("HostsUtlMain", "Checking...", None)))
        elif status in [0, 1]:
            if status:
                color, stat = "GREEN", unicode(_translate(
                    "HostsUtlMain", "[OK]", None))
            else:
                color, stat = "RED", unicode(_translate(
                    "HostsUtlMain", "[Failed]", None))
            self.set_label_color(self.Ui.labelConnStat, color)
            self.set_label_text(self.Ui.labelConnStat, stat)

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
            "HostsUtlMain", "Functions", None))
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
            item.setText(_translate("HostsUtlMain", func[3], None))
            self.Ui.Functionlist.addItem(item)

    def set_message(self, title, msg):
        """Set a message box - Public Method

        Show a message box with a specified message ({msg}) with a specified
        title ({title}).

        Args:
            title (str): A string indicating the title of the message box.
            msg (str): A string indicating the message to be shown in the
                message box.
        """
        self.Ui.FunctionsBox.setTitle(_translate(
            "HostsUtlMain", title, None))
        self.Ui.Functionlist.clear()
        item = QtGui.QListWidgetItem()
        item.setText(msg)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.Ui.Functionlist.addItem(item)

    def set_info(self):
        """Set data file info - Public Method

        Set the information of the current local data file.
        """
        info = RetrieveData.get_info()
        ver = info["Version"]
        self._cur_ver = ver
        self.set_label_text(self.Ui.labelVersionData, ver)
        build = info["Buildtime"]
        build = Utilities.timestamp_to_date(build)
        self.set_label_text(self.Ui.labelReleaseData, build)

    def set_downprogbar(self, prog, msg):
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

    def set_listitemunchecked(self, item_id):
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

    def set_cfgbytes(self, mode):
        """Set configuration byte words - Public Method

        Calculate the module configuration byte words by the selection from
        function list on the main dialog.

        Args:
            mode (str): A string indicating the operation mode for making
                hosts file.
        """
        ip_flag = self._ipv_id
        selection = {}
        if mode == "system":
            localhost_word = {
                "Windows": 0x0001, "Linux": 0x0002,
                "Unix": 0x0002, "OS X": 0x0004}[self.platform]
        else:
            localhost_word = 0x0008
        selection[0x02] = localhost_word
        ch_parts = (0x08, 0x20 if self._ipv_id else 0x10, 0x40)
        slices = self.slices[ip_flag]
        for i, part in enumerate(ch_parts):
            part_cfg = self._funcs[ip_flag][slices[i]:slices[i + 1]]
            part_word = 0
            for i, cfg in enumerate(part_cfg):
                part_word += cfg << i
            selection[part] = part_word
        self._make_cfg = selection

    def refresh_info(self, refresh=0):
        """Refresh data file information - Public Method

        Reload the data file information and show them on the main dialog. The
        information here includes both metadata and hosts module info from the
        data file.

        Arg:
            refresh (int): A flag integer indicating whether the information
                needs to be reloaded or not. 1: reload, 0: do not reload.
                Default by 0.
        """
        if refresh and RetrieveData._conn != None:
            RetrieveData.clear()
        try:
            RetrieveData.unpack()
            RetrieveData.connect_db()
            self.set_func_list(refresh)
            self.refresh_func_list()
            self.set_info()
        except (BadZipfile, IOError, OSError):
            self.warning_incorrect_datafile()

    def set_makeprog(self, mod_name, mod_num):
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
            "HostsUtlMain", "Applying module: %s(%s/%s)", None)) % (
            mod_name, mod_num, total_mods_num)
        self.Ui.Prog.setFormat(format)
        self.set_makemsg(format)

    def set_makemsg(self, msg, start=0):
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
                "HostsUtlMain", "Progress", None))
            self.Ui.Functionlist.clear()
        item = QtGui.QListWidgetItem()
        item.setText("- " + msg)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        self.Ui.Functionlist.addItem(item)

    def set_makefina(self, time, count):
        """Operations after making new hosts file - Public Method

        The slot response to the fina_trigger signal ({time}, {count}) from
        an instance of QSubMakeHosts class while making operations are
        finished.

        Args:
            time (str): A string indicating the total time uesd to make the
                new hosts file.
            count (int): An integer indicating the total number of hosts
                entries inserted into the new hosts file.
        """
        self.Ui.Functionlist.setEnabled(True)
        self.Ui.SelectIP.setEnabled(True)
        self.Ui.ButtonCheck.setEnabled(True)
        self.Ui.ButtonUpdate.setEnabled(True)
        self.Ui.ButtonApply.setEnabled(False)
        self.Ui.ButtonANSI.setEnabled(False)
        self.Ui.ButtonUTF.setEnabled(False)
        self.Ui.ButtonExit.setEnabled(True)
        RetrieveData.connect_db()
        msg = unicode(_translate("HostsUtlMain",
            "Notice: %i hosts entries has "
            "\n  been applied in %ssecs.", None)) % (count, time)
        self.set_makemsg(msg)
        self.set_downprogbar(100,
            unicode(_translate("HostsUtlMain",
                "Operation Completed Successfully!", None)))

    def finish_update(self, update):
        """Operations after checking update - Public Method

        The slot response to the trigger signal ({update}) from an instance
        of QSubChkUpdate class while checking operations are finished.

        Arg:
            update (dict): A dictionary containing metadata of the latest
                hosts file from the server.
        """
        self._update = update
        self.set_label_text(self.Ui.labelLatestData, update["version"])
        if self._update["version"] == \
                unicode(_translate("HostsUtlMain", "[Error]", None)):
            self.set_conn_status(0)
        else:
            self.set_conn_status(1)
        if self._down_flag:
            self.fetch_update_aftercheck()
        else:
            self.Ui.SelectMirror.setEnabled(True)
            self.Ui.ButtonCheck.setEnabled(True)
            self.Ui.ButtonUpdate.setEnabled(True)

    def finish_fetch(self, refresh=1, error=0):
        """Operations after downloading data file - Public Method

        The slot response to the finish_trigger signal ({refresh}, {error})
        from an instance of QSubFetchUpdate class while downloading is
        finished.

        Args:
            refresh (int): A flag integer indicating whether a refresh for
                function list is needed or not. 1: refresh, 0: no refresh.
                Default by 1.
            error (int): A flag integer indicating errors have occurred while
                downloading new data file. 1: error, 0:success. Default by 0.
        """
        self._down_flag = 0
        if error:
            # Error occurred while downloading
            self.set_downprogbar(0,
                unicode(_translate("HostsUtlMain",
                    "Error", None)))
            try:
                os.remove(self.filename)
            except:
                pass
            self.warning_download()
            msg_title = "Warning"
            msg = unicode(_translate("HostsUtlMain",
                "Incorrect Data file!\n"
                "Please use the \"Download\" key to \n"
                "fetch a new data file.", None))
            self.set_message(msg_title, msg)
            self.Ui.ButtonApply.setEnabled(False)
            self.Ui.ButtonANSI.setEnabled(False)
            self.Ui.ButtonUTF.setEnabled(False)
            self.set_conn_status(0)
        else:
            # Data file retrieved successfully
            self.set_downprogbar(100,
                unicode(_translate("HostsUtlMain",
                    "Download Complete", None)))
            self.refresh_info(refresh)
            self.Ui.ButtonApply.setEnabled(True)
            self.Ui.ButtonANSI.setEnabled(True)
            self.Ui.ButtonUTF.setEnabled(True)
        self.Ui.Functionlist.setEnabled(True)
        self.Ui.SelectMirror.setEnabled(True)
        self.Ui.ButtonCheck.setEnabled(True)
        self.Ui.ButtonUpdate.setEnabled(True)
        self.Ui.ButtonExit.setEnabled(True)

    def new_version(self):
        """Compare version of data file - Public Method

        Compare version of local data file to the version from the server.

        Returns:
            A flag integer indicating whether the local data file is
            up-to-date or not.
                1 -> The version of data file on server is newer.
                0 -> The local data file is up-to-date.
        """
        local_ver = self._cur_ver
        server_ver = self._update["version"]
        local_ver = local_ver.split('.')
        server_ver = server_ver.split('.')
        for i, ver_num in enumerate(local_ver):
            if server_ver[i] > ver_num:
                return 1
        return 0

    def warning_permission(self):
        """Show permission error warning - Public Method

        Draw permission error warning message box.
        """
        QtGui.QMessageBox.warning(
            self, _translate("HostsUtlMain", "Warning", None),
            _translate("HostsUtlMain",
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
            self, _translate("HostsUtlMain", "Warning", None),
            _translate("HostsUtlMain",
                "Error retrieving data from the server.\n"
                "Please try another server.", None))

    def warning_incorrect_datafile(self):
        """Show incorrect data file warning - Public Method

        Draw incorrect data file warning message box.
        """
        msg_title = "Warning"
        msg = unicode(_translate("HostsUtlMain",
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
        msg = unicode(_translate("HostsUtlMain",
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
        msg_title = unicode(_translate("HostsUtlMain", "Notice", None))
        msg = unicode(_translate("HostsUtlMain",
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
            self, _translate("HostsUtlMain", "Notice", None),
            _translate("HostsUtlMain", "Data file is up-to-date.", None))

    def info_complete(self):
        """Show complete message - Public Method

        Draw operation complete message box.
        """
        QtGui.QMessageBox.information(
            self, _translate("HostsUtlMain", "Complete", None),
            _translate("HostsUtlMain", "Operation completed", None))


class QSubChkConnection(QtCore.QThread):
    """A class to check connection with server

    QSubChkConnection is a subclasse of PyQt4.QtCore.QThread. This class
    contains methods to check the network connection with a specified mirror.

    The instance of this class should be created in an individual thread. And
    the object instance of MainDialog class should be set as parent here.

    Attribute:
        trigger (obj): A PyQt4.QtCore.pyqtSignal object to emit suatus signal
            to the main dialog. The meaning of the signal arguments is listed
            here:
                -1 -> checking..., 0 -> Failed, 1 -> OK.
    """
    trigger = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        """Initialize a new instance of this class - Private Method

        Get mirror settings from the main dialog to check the connection.

        Args:
            parent (obj): An instance of MainDialog object to get settings
                from.
        """
        super(QSubChkConnection, self).__init__(parent)
        self.link = parent.mirrors[parent._mirr_id]["test_url"]

    def run(self):
        """Check connection - Public Method

        Operations to check the network connection with a specified mirror.
        """
        self.trigger.emit(-1)
        status = Utilities.check_connection(self.link)
        self.trigger.emit(status)

class QSubFetchUpdate(QtCore.QThread):
    """A class to fetch the latest data file

    QSubFetchUpdate is a subclasse of PyQt4.QtCore.QThread. This class
    contains methods to retrieve the latest hosts data file.

    The instance of this class should be created in an individual thread. And
    the object instance of MainDialog class should be set as parent here.

    Attributes:
        prog_trigger (obj): A PyQt4.QtCore.pyqtSignal object to emit progress
            signal to the main dialog indicating the current download
            progress. The meaning of the signal arguments is listed here:
                (int, str) -> (progress, message)
                progress (int): An integer indicating the current download
                    progress.
                message (str): A string indicating the message to be shown to
                    users on the progress bar.
        finish_trigger (obj): A PyQt4.QtCore.pyqtSignal object to emit finish
            signal to the main dialog. The meaning of the signal arguments is
            listed here:
                (int, int) -> (refresh_flag, error_flag)
                refresh_flag (int): An integer indicating whether to refresh
                    the funcion list or not. 1: refresh, 0: do not refresh.
                error_flag (int): An integer indicating whether the
                    downloading is successfully finished or not.
                    1: error, 0: success.
    """
    prog_trigger = QtCore.pyqtSignal(int, str)
    finish_trigger = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        """Initialize a new instance of this class - Private Method

        Get download settings from the main dialog to retrieve new hosts data
        file.

        Args:
            parent (obj): An instance of MainDialog object to get settings
                from.
        """
        super(QSubFetchUpdate, self).__init__(parent)
        self.url = parent.mirrors[parent._mirr_id]["update"] + parent.filename
        self.path = "./" + parent.filename
        self.tmp_path = self.path + ".download"
        self.filesize = parent._update["size"]

    def run(self):
        """Fetch data file - Public Method

        Operations to retrieve the new hosts data file.
        """
        self.prog_trigger.emit(0, unicode(_translate(
            "HostsUtlMain", "Connecting...", None)))
        self.fetch_file(self.url, self.path)

    def fetch_file(self, url, path):
        """Fetch the data file - Public Method

        Retrieve the latest data file to a specified path ({path}) by url
        ({url}).

        Args:
            url (str): A string indicating the url to fetch the latest data
                file.
            path (str): A string indicating the path to save the data file on
                current machine.
        """
        socket.setdefaulttimeout(10)
        try:
            urllib.urlretrieve(url, self.tmp_path, self.set_progress)
            self.replace_old()
            self.finish_trigger.emit(1, 0)
        except:
            self.finish_trigger.emit(1, 1)

    def set_progress(self, done, blocksize, total):
        """Set progress bar in the main dialog - Public Method

        Send message to the main dialog to set the progress bar Prog.

        Args:
            done (int): An integer indicating the number of data blocks have
                been downloaded from the server.
            blocksize (int): An integer indicating the size of a data block.
        """
        done = done * blocksize
        if total <= 0:
            total = self.filesize
        prog = 100 * done / total
        done = Utilities.convert_size(done)
        total = Utilities.convert_size(total)
        text = unicode(_translate(
            "HostsUtlMain", "Downloading: %s / %s", None)) % (done, total)
        self.prog_trigger.emit(prog, text)

    def replace_old(self):
        """Replace the old data file - Public Method

        Overwrite the old hosts data file with the new one.
        """
        if os.path.isfile(self.path):
            os.remove(self.path)
        os.rename(self.tmp_path, self.path)


class QSubMakeHosts(QtCore.QThread):
    """A class to make a new hosts file

    QSubMakeHosts is a subclasse of PyQt4.QtCore.QThread. This class contains
    methods to make a new hosts file for client.

    The instance of this class should be created in an individual thread. And
    the object instance of MainDialog class should be set as parent here.

    Attributes:
        info_trigger (obj): A PyQt4.QtCore.pyqtSignal object to emit message
            signal to the main dialog indicating the current operation.The
            meaning of the signal arguments is listed here:
            (str, int) - (mod_name, mod_num)
            mod_name (str): A string indicating the name of a specified hosts
                module in current progress.
            mod_num (int): An integer indicating the number of current module
                in the operation sequence.
        fina_trigger (obj): A PyQt4.QtCore.pyqtSignal object to emit message
            signal to the main dialog indicating finish information. The
            meaning of the signal arguments is listed here:
            (str, int) - (time, count)
            time (str): A string indicating the total time uesd to make the
                new hosts file.
            count (int): An integer indicating the total number of hosts
                entries inserted into the new hosts file.
        move_trigger (obj): A PyQt4.QtCore.pyqtSignal object to emit signal
            to the main dialog while new hosts is being moved to specified
            path on current system. This signal does not
        count (int): An integer indicating id of the module being processed
            currently.
        mod_num (int): An integer indicating total number of modules being
            operated while making hosts file.
        make_cfg (dict): A dictionary containing the selection control bytes
            to make a hosts file.
        make_mode (str): A string indicating the operation mode for making
            hosts file.
        eol (str): A string indicating the End-Of-Line marker.
    """
    info_trigger = QtCore.pyqtSignal(str, int)
    fina_trigger = QtCore.pyqtSignal(str, int)
    move_trigger = QtCore.pyqtSignal()

    count = 0
    mod_num = 0
    make_cfg = {}
    make_mode = ""
    eol = ""

    def __init__(self, parent=None):
        """Initialize a new instance of this class - Private Method

        Fetch settings from the main dialog to make a new hosts file.

        Args:
            parent (obj): An instance of MainDialog object to get settings
                from.
        """
        super(QSubMakeHosts, self).__init__(parent)
        self.count = 0
        self.make_cfg = parent._make_cfg
        self.make_mode = parent._make_mode
        make_path = parent._make_path
        self.hostname = parent.hostname
        if parent._make_mode == "system":
            self.eol = parent._sys_eol
            self.hosts_file = open("hosts", "wb")
        elif parent._make_mode == "ansi":
            self.eol = "\r\n"
            self.hosts_file = open(unicode(make_path), "wb")
        elif parent._make_mode == "utf-8":
            self.eol = "\n"
            self.hosts_file = open(unicode(make_path), "wb")

    def run(self):
        """Make new hosts file - Public Method

        Operations to retrieve data from the data file and make the new hosts
        file for current system.
        """
        RetrieveData.connect_db()
        start_time = time.time()
        self.maketime = start_time
        self.write_head()
        self.write_info()
        self.get_hosts(self.make_cfg)
        self.hosts_file.close()
        end_time = time.time()
        total_time = "%.4f" % (end_time - start_time)
        self.fina_trigger.emit(total_time, self.count)
        if self.make_mode == "system":
            self.move_trigger.emit()
        RetrieveData.disconnect_db()

    def get_hosts(self, make_cfg):
        """Make hosts by user config - Public Method

        Make the new hosts file by the configuration ({make_cfg}) from
        function list on the main dialog.

        Args:
            make_cfg (dict): A dictionary containing module settings in byte
                word format.
        """
        for part_id in sorted(make_cfg.keys()):
            mod_cfg = make_cfg[part_id]
            if not RetrieveData.chk_mutex(part_id, mod_cfg):
                return
            mods = RetrieveData.get_ids(mod_cfg)
            for mod_id in mods:
                self.mod_num += 1
                if part_id == 0x02:
                    self.write_localhost_mod(part_id, mod_id)
                else:
                    self.write_common_mod(part_id, mod_id)

    def write_head(self):
        """Write head section - Public Method

        Write the head part of new hosts file.
        """
        for head_str in RetrieveData.get_head():
            self.hosts_file.write("%s%s" % (head_str[0], self.eol))

    def write_info(self):
        """Write info section - Public Method

        Write the information part of new hosts file.
        """
        info = RetrieveData.get_info()
        info_lines = ["#"]
        info_lines.append("# %s: %s" % ("Version", info["Version"]))
        info_lines.append("# %s: %s" % ("Buildtime", info["Buildtime"]))
        info_lines.append("# %s: %s" % ("Applytime", int(self.maketime)))
        info_lines.append("#")
        for line in info_lines:
            self.hosts_file.write("%s%s" % (line, self.eol))

    def write_common_mod(self, part_id, mod_id):
        """Write module section - Public Method

        Write hosts entries in a specified module ({mod_id}) from a specified
        part ({part_id}) of the data file to the new hosts file.

        Args:
            part_id (int): An integer indicating the index number of a part
                in the data file.
            mod_id (int): An integer indicating the index number of a module
                in the data file.
        """
        hosts, mod_name = RetrieveData.get_host(part_id, mod_id)
        self.info_trigger.emit(mod_name, self.mod_num)
        self.hosts_file.write(
            "%s# Section Start: %s%s" % (self.eol, mod_name, self.eol))
        for host in hosts:
            self.hosts_file.write("%s %s%s" % (host[0], host[1], self.eol))
            self.count += 1
        self.hosts_file.write("# Section End: %s%s" % (mod_name, self.eol))

    def write_localhost_mod(self, part_id, mod_id):
        """Write localhost section - Public Method

        Write hosts entries in a localhost module ({mod_id}) from a specified
        part ({part_id}) of the data file to the new hosts file.

        Args:
            part_id (int): An integer indicating the index number of a part
                in the data file.
            mod_id (int): An integer indicating the index number of a module
                in the data file.
        """
        hosts, mod_name = RetrieveData.get_host(part_id, mod_id)
        self.info_trigger.emit(mod_name, self.mod_num)
        self.hosts_file.write(
            "%s# Section Start: Localhost%s" % (self.eol, self.eol))
        for host in hosts:
            if "#Replace" in host[1]:
                host = (host[0], self.hostname)
            self.hosts_file.write("%s %s%s" % (host[0], host[1], self.eol))
            self.count += 1
        self.hosts_file.write("# Section End: Localhost%s" % (self.eol))


class QSubChkUpdate(QtCore.QThread):
    """A class to check update info of the latest data file

    QSubChkConnection is a subclasse of PyQt4.QtCore.QThread. This class
    contains methods to retrieve the metadata of the latest hosts data file.

    The instance of this class should be created in an individual thread. And
    the object instance of MainDialog class should be set as parent here.

    Attribute:
        trigger (obj): A PyQt4.QtCore.pyqtSignal object to emit suatus signal
            to the main dialog. The meaning of the signal is listed here:
                (dict) -> (update_info)
                update_info (dict): A dictionary containing metadata of the
                    latest hosts data file.
    """
    trigger = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize a new instance of this class - Private Method

        Get mirror settings from the main dialog to check the connection.

        Args:
            parent (obj): An instance of MainDialog object to get settings
                from.
        """
        super(QSubChkUpdate, self).__init__(parent)
        self.url = parent.mirrors[parent._mirr_id]["update"] + parent.infofile

    def run(self):
        """Check update - Public Method

        Operations to retrieve the metadata of the latest hosts data file.
        """
        try:
            socket.setdefaulttimeout(5)
            urlobj = urllib.urlopen(self.url)
            j_str = urlobj.read()
            urlobj.close()
            info = json.loads(j_str)
            self.trigger.emit(info)
        except:
            info = {"version": unicode(_translate("HostsUtlMain",
                                    "[Error]", None))}
            self.trigger.emit(info)


def qt_main():
    """Load main dialog

    Start the main dialog of Hosts Setup Utility.
    """
    trans = QtCore.QTranslator()
    trans.load("lang/en_US")
    app = QtGui.QApplication(sys.argv)
    app.installTranslator(trans)
    ui = Ui_HostsUtlMain()
    HostsUtlMain = MainDialog(ui, trans)
    ui.setupUi(HostsUtlMain)
    HostsUtlMain.set_languages()
    if not HostsUtlMain.initd:
        HostsUtlMain.init_main()
    HostsUtlMain.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    qt_main()
