#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _make.py: Make a new hosts file.
#
# Copyleft (C) 2014 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

import time
from PyQt4 import QtCore

import sys
sys.path.append("..")
from util import RetrieveData


class QSubMakeHosts(QtCore.QThread):
    """
    QSubMakeHosts is a subclass of :class:`PyQt4.QtCore.QThread`. This class
    contains methods to make a new hosts file for client.

    .. inheritance-diagram:: gui._make.QSubMakeHosts
        :parts: 1

    .. note:: The instance of this class should be created in an individual
        thread. And an instance of  class should be set as :attr:`parent`
        here.

    :ivar PyQt4.QtCore.pyqtSignal info_trigger: An instance of
        :class:`PyQt4.QtCore.pyqtSignal` to emit signal to the main dialog
        which indicates the current operation.

        .. note:: The signal :attr:`info_trigger` should be a tuple of
            (`mod_name`, mod_num`):

            * mod_name(`str`): Tag of a specified hosts module in current
              progress.
            * mod_num(`int`): Number of current module in the operation
              sequence.

    :ivar PyQt4.QtCore.pyqtSignal fina_trigger: An instance of
        :class:`PyQt4.QtCore.pyqtSignal` to emit signal to the main dialog
        which notifies statistics to the main dialog.

        .. note:: The signal :attr:`fina_trigger` should be a tuple of
            (`time`, count`):

            * time(`str`): Total time uesd while generating the new hosts
              file.
            * count(`int`): Total number of hosts entries inserted into the
              new hosts file.

        .. seealso:: Method :meth:`~gui.qdialog_d.QDialogDaemon.finish_make`
            in :class:`~gui.qdialog_d.QDialogDaemon` class.

    :ivar PyQt4.QtCore.pyqtSignal move_trigger: An instance of
        :class:`PyQt4.QtCore.pyqtSignal` to notify the main dialog while new
        hosts is being moved to specified path on current operating system.

        .. note:: This signal does not send any data.

        .. seealso:: Method :meth:`~gui.qdialog_d.QDialogDaemon.move_hosts`
            in :class:`~gui.qdialog_d.QDialogDaemon` class.

    :ivar int count: Number of the module being processed currently in the
        operation sequence.
    :ivar str make_mode: Operation mode for making hosts file. The valid value
        could be one of `system`, `ansi`, and `utf-8`.

        .. seealso:: :attr:`make_mode` in
            :class:`~gui.qdialog_d.QDialogDaemon` class.

    :ivar str hostname: File Name of hosts file.
    :ivar file hosts_file: The hosts file to write hosts to.
    :ivar dict make_cfg: Configuration to make a new hosts file.
    :ivar int mod_num: Total number of modules written to hosts file.
    :ivar str eol: End-of-Line used by the hosts file created.
    :ivar time make_time: Timestamp of making hosts file.

    .. seealso:: :class:`tui._make.MakeHosts` class.
    """
    info_trigger = QtCore.pyqtSignal(str, int)
    fina_trigger = QtCore.pyqtSignal(str, int)
    move_trigger = QtCore.pyqtSignal()

    count = 0
    make_mode = ""

    hostname = ""
    hosts_file = None
    make_cfg = {}
    mod_num = 0
    eol = ""
    make_time = None

    def __init__(self, parent):
        """
        Initialize a new instance of this class. Retrieve configuration from
        the main dialog to make a new hosts file.

        :param parent: An instance of :class:`~gui.qdialog_d.QDialogDaemon`
            class to fetch settings from.
        :type parent: :class:`~gui.qdialog_d.QDialogDaemon`

        .. warning:: :attr:`parent` MUST NOT be set as `None`.
        """
        super(QSubMakeHosts, self).__init__(parent)
        self.count = 0
        self.make_cfg = parent.make_cfg
        self.make_mode = parent.make_mode
        make_path = parent.make_path
        self.hostname = parent.hostname
        if parent.make_mode == "system":
            self.eol = parent.sys_eol
            self.hosts_file = open("hosts", "wb")
        elif parent.make_mode == "ansi":
            self.eol = "\r\n"
            self.hosts_file = open(unicode(make_path), "wb")
        elif parent.make_mode == "utf-8":
            self.eol = "\n"
            self.hosts_file = open(unicode(make_path), "wb")

    def run(self):
        """
        Start operations to retrieve data from the data file and generate new
        hosts file.
        """
        RetrieveData.connect_db()
        start_time = time.time()
        self.make_time = start_time
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
        """
        Make the new hosts file by the configuration defined by `make_cfg`
        from function list on the main dialog.

        :param make_cfg: Module settings in byte word format.
        :type make_cfg: dict

        .. seealso:: :attr:`make_cfg` in :class:`~tui.curses_d.CursesDaemon`
            class.
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
        """
        Write the head part into the new hosts file.
        """
        for head_str in RetrieveData.get_head():
            self.hosts_file.write("%s%s" % (head_str[0], self.eol))

    def write_info(self):
        """
        Write the information part into the new hosts file.
        """
        info = RetrieveData.get_info()
        info_lines = [
            "#",
            "# %s: %s" % ("Version", info["Version"]),
            "# %s: %s" % ("BuildTime", info["Buildtime"]),
            "# %s: %s" % ("ApplyTime", int(self.make_time)),
            "#"
        ]
        for line in info_lines:
            self.hosts_file.write("%s%s" % (line, self.eol))

    def write_common_mod(self, part_id, mod_id):
        """
        Write hosts entries in a module specified by `mod_id` from a part of
        the data file to the new hosts file specified by `part_id`.

        :param part_id: Index number of a part in the data file.
        :type part_id: int
        :param mod_id: Index number of a module in the data file.
        :type mod_id: int
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
        """
        Write hosts entries in a localhost module specified by `mod_id` from a
        part of the data file to the new hosts file specified by `part_id`.

        :param part_id: Index number of a part in the data file.
        :type part_id: int
        :param mod_id: Index number of a module in the data file.
        :type mod_id: int
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