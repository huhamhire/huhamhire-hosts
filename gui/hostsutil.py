#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  hostsutil.py : Main parts of Hosts Setup Utility
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
import os
import shutil
import time
from zipfile import BadZipfile
from _checkconn import QSubChkConnection
from _checkupdate import QSubChkUpdate
from _make import QSubMakeHosts
from _update import QSubFetchUpdate
from language import LangUtil
from util_ui import _translate, _fromUtf8
from util import RetrieveData, CommonUtil

__version__ = "1.9.7"
__revision__ = "$Id$"
__author__ = "huhamhire <me@huhamhire.com>"

import sys

from PyQt4 import QtCore, QtGui

from util_ui import Ui_Util
from qdialog_ui import QDialogUI

# Path to store language files
LANG_DIR = "./gui/lang/"

class HostsUtil(QDialogUI):
    """A class to manage the operations and UI of Hosts Setup Utility

    HostsUtil class is a subclasse of PyQt4.QtGui.QDialog which is used to
    make the main dialog of this hosts setup utility.
    This class contains a set of tools used to manage the operations while
    modifying the hosts file of current operating system. Including methods
    to manage operations to update data file, download data file, configure
    hosts, make hosts file, backup hosts file, and restore backup.
    The HostsUtil class also provides QT slots to deal with the QT singles
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
        plat_flag (bool): A boolean flag indicating whether the current os is
            supported or not.
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
    plat_flag = True
    hostname = ''
    hostspath = ''
    # Mirror related configuration
    _mirr_id = 0
    mirrors = []
    # Name of items from the function list to be localized
    __list_trans = [
        _translate("Util", "google(cn)", None),
        _translate("Util", "google(hk)", None),
        _translate("Util", "google(us)", None),
        _translate("Util", "google-apis(cn)", None),
        _translate("Util", "google-apis(us)", None),
        _translate("Util", "activation-helper", None),
        _translate("Util", "facebook", None),
        _translate("Util", "twitter", None),
        _translate("Util", "youtube", None),
        _translate("Util", "wikipedia", None),
        _translate("Util", "institutions", None),
        _translate("Util", "steam", None),
        _translate("Util", "others", None),
        _translate("Util", "adblock-hostsx", None),
        _translate("Util", "adblock-mvps", None),
        _translate("Util", "adblock-mwsl", None),
        _translate("Util", "adblock-yoyo", None),
        ]
    # Data file related configuration
    filename = "hostslist.data"
    infofile = "hostsinfo.json"

    def __init__(self, trans):
        """Initialize a new instance of this class - Private Method

        Set the UI object and current translator of the main dialog.

        Args:
            Ui (obj): A user interface object indicating the main dialog of
                this program.
            trans (obj): A PyQt4.QtCore.QTranslator object indicating the
                current UI language setting.
        """
        super(HostsUtil, self).__init__()
        self._trans = trans
        self.set_platform()
        self.set_style()
        self.set_stylesheet()

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
            if not RetrieveData.db_exists():
                self.warning_no_datafile()
            else:
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
        new_lang = LangUtil.get_locale_by_language(unicode(lang))
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
            self, _translate("Util", "Backup hosts", None),
            QtCore.QString(filename),
            _translate("Util", "Backup File(*.bak)", None))
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
            self, _translate("Util", "Restore hosts", None),
            QtCore.QString(filename),
            _translate("Util", "Backup File(*.bak)", None))
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
            self.set_update_click_btns()
        if self._update == {} or self._update["version"] == \
            unicode(_translate("Util", "[Error]", None)):
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
        self.set_fetch_click_btns()
        self._down_flag = 1
        if self._update == {} or self._update["version"] == \
            unicode(_translate("Util", "[Error]", None)):
            self.check_update()
        elif self.new_version():
            self.fetch_update()
        else:
            self.info_uptodate()
            self.finish_fetch()

    def on_LinkActivated(self, url):
        """Open external link in browser - Public Method

        The slot response to the signal from Label widget while the text with
        a hyperlink is clicked by user.
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def init_main(self):
        """Initialize the main dialog - Public Method

        Set up the elements on the main dialog. Check the environment of
        current operating system and current session.
        """
        self.Ui.SelectMirror.clear()
        # Set mirrors
        self.mirrors = CommonUtil.set_network("network.conf")
        for i, mirror in enumerate(self.mirrors):
            self.Ui.SelectMirror.addItem(_fromUtf8(""))
            self.Ui.SelectMirror.setItemText(
                i, _translate("Util", mirror["tag"], None))
        self.set_platform_label()
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
        super(HostsUtil, self).close()

    def check_root(self):
        """Check root privileges - Public Method

        Check if current session is ran with root privileges.
        """
        is_root = CommonUtil.check_privileges()[1]
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
        self.set_update_start_btns()
        self.set_label_text(self.Ui.labelLatestData, unicode(
            _translate("Util", "Checking...", None)))
        thread = QSubChkUpdate(self)
        thread.trigger.connect(self.finish_update)
        thread.start()

    def fetch_update(self):
        """Operations to fetch new data file - Public Method

        Call operations to retrieve a new hosts data file from a server.
        """
        self.set_fetch_start_btns()
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
            unicode(_translate("Util", "[Error]", None)):
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
            self, _translate("Util", "Export hosts", None),
            QtCore.QString(filename),
            _translate("Util", "hosts File", None))
        return filepath

    def make_hosts(self, mode="system"):
        """Operations to make hosts file - Public Method

        Call operations to make a new hosts file for current system.

        Args:
            mode (str): A string indicating the operation mode for making
                hosts file.
        """
        self.set_make_start_btns()
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
        msg = unicode(_translate("Util",
            "Copying new hosts file to\n"
            "  %s", None)) % self.hostspath
        self.set_makemsg(msg)
        try:
            shutil.copy2(filepath, self.hostspath)
        except IOError:
            self.warning_permission()
            os.remove(filepath)
            return
        except OSError:
            pass
        msg = unicode(_translate("Util",
            "Remove temporary file", None))
        self.set_makemsg(msg)
        os.remove(filepath)
        msg = unicode(_translate("Util",
            "Operation completed", None))
        self.set_makemsg(msg)
        self.info_complete()

    def set_platform(self):
        """Set OS info - Public Method

        Set the information of current operating system platform.
        """
        system, hostname, path, encode, flag = CommonUtil.check_platform()
        self.platform = system
        self.hostname = hostname
        self.hostspath = path
        self.plat_flag = flag
        if encode == "win_ansi":
            self._sys_eol = "\r\n"
        else:
            self._sys_eol = "\n"

    def mouseMoveEvent(self, e):
        """Set mouse drag event - Public Method

        Allow drag operations to set the new position for current dialog.

        Args:
            e (QMouseEvent): A QMouseEvent object indicating current mouse
                event.
        """
        if e.buttons() & QtCore.Qt.LeftButton:
            try:
                self.move(e.globalPos() - self.dragPos)
            except AttributeError:
                pass
            e.accept()

    def mousePressEvent(self, e):
        """Set mouse press event - Public Method

        Allow drag operations to set the new position for current dialog.

        Args:
            e (QMouseEvent): A QMouseEvent object indicating current mouse
                event.
        """
        if e.button() == QtCore.Qt.LeftButton:
            self.dragPos = e.globalPos() - self.frameGeometry().topLeft()
            e.accept()

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
        ch_parts = (0x08, 0x20 if ip_flag else 0x10, 0x40)
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
        self.set_make_finish_btns()
        RetrieveData.connect_db()
        msg = unicode(_translate("Util",
            "Notice: %i hosts entries has "
            "\n  been applied in %ssecs.", None)) % (count, time)
        self.set_makemsg(msg)
        self.set_downprogbar(100,
            unicode(_translate("Util",
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
                unicode(_translate("Util", "[Error]", None)):
            self.set_conn_status(0)
        else:
            self.set_conn_status(1)
        if self._down_flag:
            self.fetch_update_aftercheck()
        else:
            self.set_update_finish_btns()

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
                unicode(_translate("Util", "Error", None)))
            try:
                os.remove(self.filename)
            except:
                pass
            self.warning_download()
            msg_title = "Warning"
            msg = unicode(_translate("Util",
                "Incorrect Data file!\n"
                "Please use the \"Download\" key to \n"
                "fetch a new data file.", None))
            self.set_message(msg_title, msg)
            self.set_conn_status(0)
        else:
            # Data file retrieved successfully
            self.set_downprogbar(100,
                unicode(_translate("Util",
                    "Download Complete", None)))
            self.refresh_info(refresh)
        self.set_fetch_finish_btns(error)

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

def qt_main():
    """Load main dialog

    Start the main dialog of Hosts Setup Utility.
    """
    trans = QtCore.QTranslator()
    trans.load(LANG_DIR + "en_US")
    app = QtGui.QApplication(sys.argv)
    app.installTranslator(trans)
    HostsUtlMain = HostsUtil(trans)
    HostsUtlMain.set_languages()
    if not HostsUtlMain.initd:
        HostsUtlMain.init_main()
    HostsUtlMain.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    qt_main()
