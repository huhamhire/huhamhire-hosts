#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  qdialog_d.py : Operations on the main dialog.
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
    QDialogDaemon class contains methods used to manage the operations while
    modifying the hosts file of current operating system. Including methods
    to manage operations to update data file, download data file, configure
    hosts, make hosts file, backup hosts file, and restore backup.

    .. note:: This class is subclass of :class:`~gui.qdialog_ui.QDialogUI`
        class and parent class of :class:`~gui.qdialog_slots.QDialogSlots`.

    :ivar int_down_flag: An flag indicating the downloading status of
        current session. 1 represents data file is being downloaded.
    :ivar dict _update: Update information of the current data file on server.
    :ivar int _writable: Indicating whether the program is run with admin/root
        privileges. The value could be `1` or `0`.

        .. seealso:: `_update` and `_writable` in
            :class:`~tui.curses_d.CursesDaemon` class.

    :ivar list _funcs: Two lists with the information of function list both
        for IPv4 and IPv6 environment.
    :ivar list choice: Two lists with the selection of functions both
        for IPv4 and IPv6 environment.
    :ivar list slices: Two lists with integers indicating the number of
        function items from different parts listed in the function list.

        .. seealso:: `_funcs`, `choice`, and `slices` in
            :class:`~tui.curses_ui.CursesUI` class.

    :ivar dict make_cfg: A set of module selection control bytes used to
        control whether a specified method is used or not while generate a
        hosts file.

        .. seealso:: :attr:`make_cfg` in
            :class:`~tui.curses_d.CursesDaemon` class.
    :ivar str platform: Platform of current operating system. The value could
        be `Windows`, `Linux`, `Unix`, `OS X`, and of course `Unknown`.
    :ivar str hostname: The hostname of current operating system.

        .. note:: This attribute would only be used on linux.

    :ivar str hosts_path: The absolute path to the hosts file on current
        operating system.
    :ivar str make_mode: Operation mode for making hosts file. The valid value
        could be one of `system`, `ansi`, and `utf-8`.

        .. seealso:: :attr:`make_mode` in
            :class:`~util.makehosts.MakeHosts` class.

    :ivar str sys_eol: The End-Of-Line marker. This maker could typically be
        one of `CR`, `LF`, or `CRLF`.

        .. seealso:: :attr:`sys_eol` in
            :class:`~tui.curses_ui.CursesUI` class.
    """
    _down_flag = 0

    _update = {}
    _writable = 0

    _funcs = [[], []]
    choice = [[], []]
    slices = [[], []]
    make_cfg = {}
    platform = ''
    hostname = ''
    hosts_path = ''
    sys_eol = ''

    make_mode = ''

    def __init__(self):
        super(QDialogDaemon, self).__init__()
        self.set_platform()
        self.set_platform_label()

    def check_writable(self):
        """
        Check if current session is ran with root privileges.

        .. note:: IF current session does not has the write privileges to the
            hosts file of current system, a warning message box would popup.

        .. note:: ALL operation would change the `hosts` file on current
            system could only be done while current session has write
            privileges to the file.
        """
        writable = CommonUtil.check_privileges()[1]
        self._writable = writable
        if not writable:
            self.warning_permission()

    def check_connection(self):
        """
        Operations to check the connection to current server.
        """
        thread = QSubChkConnection(self)
        thread.trigger.connect(self.set_conn_status)
        thread.start()

    def check_update(self):
        """
        Retrieve the metadata of the latest data file from a server.
        """
        self.set_update_start_btns()
        self.set_label_text(self.ui.labelLatestData, unicode(
            _translate("Util", "Checking...", None)))
        thread = QSubChkUpdate(self)
        thread.trigger.connect(self.finish_update)
        thread.start()

    def fetch_update(self):
        """
        Retrieve a new hosts data file from a server.
        """
        self.set_fetch_start_btns()
        thread = QSubFetchUpdate(self)
        thread.prog_trigger.connect(self.set_down_progress)
        thread.finish_trigger.connect(self.finish_fetch)
        thread.start()

    def fetch_update_after_check(self):
        """
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
        """
        Display the export dialog and get the path to save the exported hosts
        file.

        :return: Path to export a hosts file.
        :rtype: str
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
        """
        Make a new hosts file for current system.

        :param mode: Operation mode for making hosts file. The valid value
            could be one of `system`, `ansi`, and `utf-8`.
            Default by `system`.
        :type mode: str
        """
        self.set_make_start_btns()
        self.set_make_message(unicode(_translate(
            "Util", "Building hosts file...", None)), 1)
        # Avoid conflict while making hosts file
        RetrieveData.disconnect_db()
        self.make_mode = mode
        self.set_config_bytes(mode)
        thread = QSubMakeHosts(self)
        thread.info_trigger.connect(self.set_make_progress)
        thread.fina_trigger.connect(self.finish_make)
        thread.move_trigger.connect(self.move_hosts)
        thread.start()

    def move_hosts(self):
        """
        Move hosts file to the system path after making.

        .. note:: This method is the slot responses to the move_trigger signal
            from an instance of :class:`~gui._make.QSubMakeHosts` class while
            making operations are finished.

        .. seealso:: :attr:`move_trigger` in
            :class:`~gui._make.QSubMakeHosts`.
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
        """
        Set the information of current operating system platform.
        """
        system, hostname, path, encode, flag = CommonUtil.check_platform()
        self.platform = system
        self.hostname = hostname
        self.hosts_path = path
        self.plat_flag = flag
        if encode == "win_ansi":
            self.sys_eol = "\r\n"
        else:
            self.sys_eol = "\n"

    def set_config_bytes(self, mode):
        """
        Generate the module configuration byte words by the selection from
        function list on the main dialog.

        :param mode: Operation mode for making hosts file. The valid value
            could be one of `system`, `ansi`, and `utf-8`.

            .. seealso:: Method
                :meth:`~gui.qdialog_d.QDialogDaemon.make_hosts`.
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
        ch_parts = [0x08, 0x20 if ip_flag else 0x10, 0x40]
        # Set customized module if exists
        if os.path.isfile(self.custom):
            ch_parts.insert(0, 0x04)
        slices = self.slices[ip_flag]
        for i, part in enumerate(ch_parts):
            part_cfg = self._funcs[ip_flag][slices[i]:slices[i + 1]]
            part_word = 0
            for i, cfg in enumerate(part_cfg):
                part_word += cfg << i
            selection[part] = part_word
        self.make_cfg = selection

    def refresh_info(self, refresh=0):
        """
        Reload the data file information and show them on the main dialog. The
        information here includes both metadata and hosts module info from the
        data file.

        :param refresh: A flag indicating whether the information on main
            dialog needs to be reloaded or not. The value could be `0` or `1`.

                =======  =============
                refresh  operation
                =======  =============
                0        Do NOT reload
                1        Reload
                =======  =============

        :type refresh: int
        """
        if refresh and RetrieveData.conn is not None:
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
        """
        Start operations after making new hosts file.

        .. note:: This method is the slot responses to the fina_trigger signal
            values :attr:`time`, :attr:`count` from an instance of
            :class:`~gui._make.QSubMakeHosts` class while making operations
            are finished.

        :param time: Total time uesd while generating the new hosts file.
        :type time: str
        :param count: Total number of hosts entries inserted into the new
            hosts file.
        :type count: int

        .. seealso:: :attr:`fina_trigger` in
            :class:`~gui._make.QSubMakeHosts` class.
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
        """
        Start operations after checking update.

        .. note:: This method is the slot responses to the trigger signal
            value :attr:`update` from an instance of
            :class:`~gui._checkupdate.QSubChkUpdate` class while checking
            operations are finished.

        :param update: Metadata of the latest hosts data file on the server.
        :type update: dict

        .. seealso:: :attr:`trigger` in
            :class:`~gui._checkupdate.QSubChkUpdate` class.
        """
        self._update = update
        self.set_label_text(self.ui.labelLatestData, update["version"])
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
        """
        Start operations after downloading data file.

        .. note:: This method is the slot responses to the finish_trigger
            signal :attr:`refresh`, :attr:`error` from an instance of
            :class:`~gui._update.QSubFetchUpdate` class while downloading is
            finished.

        :param refresh: An flag indicating whether the downloading progress is
            successfully finished or not. Default by 1.
        :type refresh: int.
        :param error: An flag indicating whether the downloading
              progress is successfully finished or not. Default by 0.
        :type error: int

        .. seealso:: :attr:`finish_trigger` in
            :class:`~gui._update.QSubFetchUpdate` class.
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
        """
        Compare version of local data file to the version from the server.

        :return: A flag indicating whether the local data file is up-to-date
            or not.
        :rtype: int

                ======  ============================================
                Return  File status
                ======  ============================================
                1       The version of data file on server is newer.
                0       The local data file is up-to-date.
                ======  ============================================
        """
        local_ver = self._cur_ver
        server_ver = self._update["version"]
        local_ver = local_ver.split('.')
        server_ver = server_ver.split('.')
        for i, ver_num in enumerate(local_ver):
            if server_ver[i] > ver_num:
                return 1
        return 0