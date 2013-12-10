#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  qdialog_d.py : Main parts of Hosts Setup Utility
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

__author__ = "huhamhire <me@huhamhire.com>"

import os
import shutil

from zipfile import BadZipfile
from PyQt4 import QtCore, QtGui

from _checkconn import QSubChkConnection
from _checkupdate import QSubChkUpdate
from _make import QSubMakeHosts
from _update import QSubFetchUpdate
from qdialog_ui import QDialogUI
from util_ui import _translate

import sys
sys.path.append("..")
from util import RetrieveData, CommonUtil


class QDialogDaemon(QDialogUI):
    """
    Attributes:
        _down_flag (int) An integer indicating the downloading status of
            current session. 1 represents data file is being downloaded.
        _make_cfg (dict): A dictionary containing the selection control bytes
            to make a hosts file.
        _make_mode (str): A string indicating the operation mode for making
            hosts file.
        _sys_eol (str): A string indicating the End-Of-Line marker.
        _update (dict): A dictionary containing the update information of the
            current data file on server.
        _writable (int): An integer indicating whether the program is run with
            admin/root privileges. The value could be 1 or 0.

        hostname (str): A string indicating the hostname of current operating
            system. This attribute would be used for linux clients.
        hosts_path (str): A string indicating the absolute path of the hosts
            file on current operating system.
    """

    _down_flag = 0
    _make_cfg = {}
    _make_mode = ""
    _sys_eol = ""
    _update = {}
    _writable = 0

    hostname = ''
    hosts_path = ''

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
        super(QDialogDaemon, self).close()

    def check_writable(self):
        """Check root privileges - Public Method

        Check if current session is ran with root privileges.
        """
        writable = CommonUtil.check_privileges()[1]
        self._writable = writable
        if not writable:
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
        thread.prog_trigger.connect(self.set_down_progress)
        thread.finish_trigger.connect(self.finish_fetch)
        thread.start()

    def fetch_update_after_check(self):
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
        self.set_make_message(unicode(_translate(
            "Util", "Building hosts file...", None)), 1)
        # Avoid conflict while making hosts file
        RetrieveData.disconnect_db()
        self._make_mode = mode
        self.set_config_bytes(mode)
        thread = QSubMakeHosts(self)
        thread.info_trigger.connect(self.set_make_progress)
        thread.fina_trigger.connect(self.finish_make)
        thread.move_trigger.connect(self.move_hosts)
        thread.start()

    def move_hosts(self):
        """Move hosts file to the system path after making - Public Method

        The slot response to the move_trigger signal from an instance of
        QSubMakeHosts class while making operations are finished.
        """
        filepath = "hosts"
        msg = unicode(
            _translate("Util", "Copying new hosts file to\n"
                               "%s", None)) % self.hosts_path
        self.set_make_message(msg)
        try:
            shutil.copy2(filepath, self.hosts_path)
        except IOError:
            self.warning_permission()
            os.remove(filepath)
            return
        except OSError:
            pass
        msg = unicode(
            _translate("Util", "Remove temporary file", None))
        self.set_make_message(msg)
        os.remove(filepath)
        msg = unicode(
            _translate("Util", "Operation completed", None))
        self.set_make_message(msg)
        self.info_complete()

    def set_platform(self):
        """Set OS info - Public Method

        Set the information of current operating system platform.
        """
        system, hostname, path, encode, flag = CommonUtil.check_platform()
        self.platform = system
        self.hostname = hostname
        self.hosts_path = path
        self.plat_flag = flag
        if encode == "win_ansi":
            self._sys_eol = "\r\n"
        else:
            self._sys_eol = "\n"

    def set_config_bytes(self, mode):
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
        if refresh and RetrieveData.conn is None:
            RetrieveData.clear()
        try:
            RetrieveData.unpack()
            RetrieveData.connect_db()
            self.set_func_list(refresh)
            self.refresh_func_list()
            self.set_info()
        except (BadZipfile, IOError, OSError):
            self.warning_incorrect_datafile()

    def finish_make(self, time, count):
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
        msg = unicode(
            _translate("Util", "Notice: %i hosts entries has "
                               "\n  been applied in %ssecs.", None))\
            % (count, time)
        self.set_make_message(msg)
        self.set_down_progress(100, unicode(
            _translate("Util", "Operation Completed Successfully!", None)))

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
            self.fetch_update_after_check()
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
            self.set_down_progress(0, unicode(
                _translate("Util", "Error", None)))
            try:
                os.remove(self.filename)
            except:
                pass
            self.warning_download()
            msg_title = "Warning"
            msg = unicode(
                _translate("Util", "Incorrect Data file!\n"
                                   "Please use the \"Download\" key to \n"
                                   "fetch a new data file.", None))
            self.set_message(msg_title, msg)
            self.set_conn_status(0)
        else:
            # Data file retrieved successfully
            self.set_down_progress(100, unicode(
                _translate("Util", "Download Complete", None)))
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