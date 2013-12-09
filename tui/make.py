#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  make.py:
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
    mod_num = 0
    make_cfg = {}
    eol = ""

    def __init__(self, parent=None):
        """Initialize a new instance of this class - Private Method

        Fetch settings from the main dialog to make a new hosts file.

        Args:
            parent (obj): An instance of MainDialog object to get settings
                from.
        """
        self.make_cfg = parent._make_cfg
        self.hostname = parent.hostname
        self.eol = parent._sys_eol
        self.hosts_file = open("hosts", "wb")

    def make(self):
        """Make new hosts file - Public Method

        Operations to retrieve data from the data file and make the new hosts
        file for current system.
        """
        RetrieveData.connect_db()
        self.maketime = time.time()
        self.write_head()
        self.write_info()
        self.get_hosts(self.make_cfg)
        self.hosts_file.close()
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
        self.hosts_file.write(
            "%s# Section Start: %s%s" % (self.eol, mod_name, self.eol))
        for host in hosts:
            self.hosts_file.write("%s %s%s" % (host[0], host[1], self.eol))
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
        self.hosts_file.write(
            "%s# Section Start: Localhost%s" % (self.eol, self.eol))
        for host in hosts:
            if "#Replace" in host[1]:
                host = (host[0], self.hostname)
            self.hosts_file.write("%s %s%s" % (host[0], host[1], self.eol))
        self.hosts_file.write("# Section End: Localhost%s" % self.eol)
