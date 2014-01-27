#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  makehosts.py: Make a hosts file.
#
# Copyleft (C) 2014 - huhamhire <me@huhamhire.com>
# =====================================================================
# Licensed under the GNU General Public License, version 3. You should
# have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
# =====================================================================

__author__ = "huhamhire <me@huhamhire.com>"

import os
import time

from retrievedata import RetrieveData


class MakeHosts(object):
    """
    MakeHosts class contains methods to make a hosts file with host entries
    from a single data file.

    :ivar str make_mode: Operation mode for making hosts file. The valid value
        could be one of `system`, `ansi`, and `utf-8`.

        .. seealso:: :attr:`make_mode` in
            :class:`~gui.qdialog_d.QDialogDaemon` class.

    :ivar str custom: File name of User Customized Hosts file.

        .. seealso:: :ref:`User Customized Hosts<intro-customize>`.

    :ivar str hostname: File Name of hosts file.
    :ivar file hosts_file: The hosts file to write hosts to.
    :ivar int mod_num: Total number of modules written to hosts file.
    :ivar int count: Number of the module being processed currently in the
        operation sequence.
    :ivar dict make_cfg: Configuration to make a new hosts file.
    :ivar str eol: End-of-Line used by the hosts file created.
    :ivar time make_time: Timestamp of making hosts file.

    .. seealso:: :class:`gui._make.QSubMakeHosts` class and
        :class:`tui.curses_d.CursesDaemon` class.
    """
    make_mode = ""
    custom = ""
    hostname = ""
    hosts_file = None
    make_cfg = {}
    mod_num = 0
    count = 0
    eol = ""
    make_time = None

    def __init__(self, parent):
        """
        Retrieve configuration from the main dialog to make a new hosts file.

        :param parent: An instance of :class:`~tui.curses_d.CursesDaemon`
            class to retrieve configuration with.
        :type parent: :class:`~tui.curses_d.CursesDaemon`

        .. warning:: :attr:`parent` MUST NOT be set as `None`.
        """
        self.count = 0
        self.make_cfg = parent.make_cfg
        self.hostname = parent.hostname
        self.custom = parent.custom
        make_path = parent.make_path
        self.make_mode = parent.make_mode
        if self.make_mode == "system":
            self.eol = parent.sys_eol
            self.hosts_file = open("hosts", "wb")
        elif self.make_mode == "ansi":
            self.eol = "\r\n"
            self.hosts_file = open(unicode(make_path), "wb")
        elif self.make_mode == "utf-8":
            self.eol = "\n"
            self.hosts_file = open(unicode(make_path), "wb")

    def make(self):
        """
        Start operations to retrieve data from the data file and make the new
        hosts file for the current operating system.
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
                hosts, mod_name = RetrieveData.get_host(part_id, mod_id)
                if part_id == 0x02:
                    self.write_localhost_mod(hosts)
                elif part_id == 0x04:
                    self.write_customized()
                else:
                    self.write_common_mod(hosts, mod_name)

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

    def write_common_mod(self, hosts, mod_name):
        """
        Write hosts entries :attr:`hosts` from a module named `hosts` in the
        hosts data file..

        :param hosts: Hosts entries from a part in the data file.
        :type hosts: list
        :param mod_name: Name of a module from the data file.
        :type mod_name: str
        """
        self.hosts_file.write(
            "%s# Section Start: %s%s" % (self.eol, mod_name, self.eol))
        for host in hosts:
            ip = host[0]
            if len(ip) < 16:
                ip = ip.ljust(16)
            self.hosts_file.write("%s %s%s" % (ip, host[1], self.eol))
            self.count += 1
        self.hosts_file.write("# Section End: %s%s" % (mod_name, self.eol))

    def write_customized(self):
        """
        Write user customized hosts list into the hosts file if the customized
        hosts file exists.
        """
        if os.path.isfile(self.custom):
            custom_file = open(unicode(self.custom), "r")
            lines = custom_file.readlines()
            self.hosts_file.write(
                "%s# Section Start: Customized%s" % (self.eol, self.eol))
            for line in lines:
                line = line.strip("\n")
                entry =  line.split(" ", 1)
                if line.startswith("#"):
                    self.hosts_file.write(line + self.eol)
                elif len(entry) > 1:
                    ip = entry[0]
                    if len(ip) < 16:
                        ip = entry[0].ljust(16)
                    self.hosts_file.write(
                        "%s %s%s" % (ip, entry[1], self.eol)
                    )
                else:
                    pass
            self.hosts_file.write("# Section End: Customized%s" % self.eol)

    def write_localhost_mod(self, hosts):
        """
        Write localhost entries :attr:`hosts` into the hosts file.

        :param hosts: Hosts entries from a part in the data file.
        :type hosts: list
        """
        self.hosts_file.write(
            "%s# Section Start: Localhost%s" % (self.eol, self.eol))
        for host in hosts:
            if "#Replace" in host[1]:
                host = (host[0], self.hostname)
            ip = host[0]
            if len(ip) < 16:
                ip = ip.ljust(16)
            self.hosts_file.write("%s %s%s" % (ip, host[1], self.eol))
            self.count += 1
        self.hosts_file.write("# Section End: Localhost%s" % self.eol)