#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  _make.py: Make a hosts file.
#
# Copyleft (C) 2014 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

import sys
import time

sys.path.append("..")
from util import RetrieveData


class MakeHosts(object):
    """
    MakeHosts class contains methods to make a hosts file with host entries
    from a single data file.

    :ivar str hostname: File Name of hosts file.
    :ivar file hosts_file: The hosts file to write hosts to.
    :ivar int mod_num: Number of modules written to hosts file.
    :ivar dict make_cfg: Configuration to make a new hosts file.
    :ivar str eol: End-of-Line used by the hosts file created.
    :ivar time make_time: Timestamp of making hosts file.
    """
    hostname = ""
    hosts_file = None
    make_cfg = {}
    mod_num = 0
    eol = ""
    make_time = None

    def __init__(self, parent=None):
        """
        Retrieve configuration from the main dialog to make a new hosts file.

        :param parent: An instance of :class:`~tui.curses_d.CursesDaemon`
            class to get configuration with.
        :type parent: :class:`~tui.curses_d.CursesDaemon`
        """
        self.make_cfg = parent.make_cfg
        self.hostname = parent.hostname
        self.eol = parent.sys_eol
        self.hosts_file = open("hosts", "wb")

    def make(self):
        """
        Operations to retrieve data from the data file and make the new hosts
        file for the current operating system.
        """
        RetrieveData.connect_db()
        self.make_time = time.time()
        self.write_head()
        self.write_info()
        self.get_hosts(self.make_cfg)
        self.hosts_file.close()
        RetrieveData.disconnect_db()

    def get_hosts(self, make_cfg):
        """
        Make the new hosts file by the configuration defined by `make_cfg`
        from function list on the main dialog.

        :param make_cfg: Module settings in byte word format.
        :type make_cfg: dict
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
        Write the head part of new hosts file.
        """
        for head_str in RetrieveData.get_head():
            self.hosts_file.write("%s%s" % (head_str[0], self.eol))

    def write_info(self):
        """
        Write the information part of new hosts file.
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
        self.hosts_file.write(
            "%s# Section Start: %s%s" % (self.eol, mod_name, self.eol))
        for host in hosts:
            self.hosts_file.write("%s %s%s" % (host[0], host[1], self.eol))
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
        self.hosts_file.write(
            "%s# Section Start: Localhost%s" % (self.eol, self.eol))
        for host in hosts:
            if "#Replace" in host[1]:
                host = (host[0], self.hostname)
            self.hosts_file.write("%s %s%s" % (host[0], host[1], self.eol))
        self.hosts_file.write("# Section End: Localhost%s" % self.eol)
