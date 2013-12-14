#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _make.py:
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
    """A class to make a new hosts file

    QSubMakeHosts is a subclasse of PyQt4.QtCore.QThread. This class contains
    methods to make a new hosts file for client.

    The instance of this class should be created in an individual thread. And
    the object instance of HostsUtil class should be set as parent here.

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
            parent (obj): An instance of HostsUtil object to get settings
                from.
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