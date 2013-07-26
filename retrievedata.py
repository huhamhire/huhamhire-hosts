#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# retrievedata.py : Read data from the hosts data file
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

__version__ = "0.8"
__revision__ = "$Id$"
__author__ = "huhamhire <me@huhamhire.com>"

__all__ = ["RetrieveData", "make_hosts"]

import os
import sqlite3
import time
import zipfile

class RetrieveData(object):
    """A class to fetch data from data file

    RetrieveData class contains a set of tools to retrieve information from
    the hosts data file. All methods from this class are defined as class
    methods.

    Attributes:
        _conn (obj): An instance of sqlite3.connect object to set the
            connection with a SQLite database.
        _cur (obj): An instance of sqlite3.connect.cursor object to operate
            SQL queries in the database.
        _database (str): A string indicating the filename of a SQLite database
            file.
    """
    _conn = None
    _cur = None
    _database = None

    @classmethod
    def connect_db(cls, database="hostslist.s3db"):
        """Connect to database - Class Method

        Set up connection with a SQLite database.

        Args:
            database (str): A string indicating the SQLite database file.
                "hostslist.s3db" by default.
        """
        cls._conn = sqlite3.connect(database)
        cls._cur = cls._conn.cursor()
        cls._database = database

    @classmethod
    def disconnect_db(cls):
        """Disconnect to database - Class Method

        Close the connection with a SQLite database.
        """
        cls._conn.close()

    @classmethod
    def get_info(cls):
        """Get data file information - Class Method

        Retrieve the metadata of current data file.

        Returns:
            A dictionary containing the metadata of current data file.
        """
        cls._cur.execute("SELECT sect, info FROM info")
        info = dict(cls._cur.fetchall())
        return info

    @classmethod
    def get_head(cls):
        """Get head info from data file - Class Method

        Retrieve the head information from hosts data file.

        Returns:
            A list containing hosts head information.
        """
        cls._cur.execute("SELECT str FROM hosts_head ORDER BY ln")
        head = cls._cur.fetchall()
        return head

    @classmethod
    def get_ids(cls, id_cfg):
        """Get id numbers - Class Method

        Calculate the id numbers covered by config word ({id_cfg}).

        Args:
            id_cfg (int): A hex number indicating the config word of id
                selections.

        Returns:
            A list containing the id numbers covered by config word.
        """
        cfg = bin(id_cfg)[:1:-1]
        ids = []
        for i, id_en in enumerate(cfg):
            if int(id_en):
                ids.append(0b1 << i)
        return ids

    @classmethod
    def get_host(cls, part_id, mod_id):
        """Get hosts entries - Class Method

        Retrieve the hosts of a specified module ({mod_id}) from a specified
        part ({part_id}) in the data file.

        Args:
            part_id (int): An integer indicating the id number of a specified
                part from the hosts data file
            mod_id (int): An integer indicating the id number of a specified
                module number from a specified part.

        Returns:
            (hosts, mod_name)
            hosts (list): A list containing hosts entries of a specified
                module.
            mod_name (str): A string indicating the name of a specified
                module.
        """
        cls._cur.execute("SELECT part_name FROM parts "
                "WHERE part_id=%s" % part_id)
        part_name = cls._cur.fetchone()[0]
        cls._cur.execute("SELECT ip, host FROM %s "
                "WHERE cate=%s" % (part_name, mod_id))
        hosts = cls._cur.fetchall()
        cls._cur.execute("SELECT mod_name FROM modules "
                "WHERE part_id=%s AND mod_id = %s" % (part_id, mod_id))
        mod_name = cls._cur.fetchone()[0]
        return hosts, mod_name

    @classmethod
    def get_choice(cls, flag_v6=False):
        """Get module selection choices - Class Method

        Retrieve module selection items from the hosts data file with default
        selection for users.

        Args:
            flag_v6 (bool): A bool flag indicating whether to receive the IPv6
                entries or the IPv4 ones. True: IPv6, False: IPv4.

        Returns:
            (modules, defaults, slices)
            modules (list): A list containing information of modules for users
                to select.
            defaults (dict): A dictionary containing default selection for
                selected parts.
            slices (list): A list containing the number of modules in each
                part.
        """
        ch_parts = (0x08, 0x20 if flag_v6 else 0x10, 0x40)
        cls._cur.execute("SELECT * FROM modules "
                "WHERE part_id IN (?, ?, ?)", ch_parts)
        modules = cls._cur.fetchall()
        cls._cur.execute("SELECT part_id, part_default FROM parts "
                "WHERE part_id IN (?, ?, ?)", ch_parts)
        default_cfg = cls._cur.fetchall()
        defaults = {}
        for default in default_cfg:
            defaults[default[0]] = cls.get_ids(default[1])
        slices = [0]
        for ch_part in ch_parts:
            cls._cur.execute("SELECT COUNT(mod_id) FROM modules "
                    "WHERE part_id=?", (ch_part, ))
            slices.append(cls._cur.fetchone()[0])
        for s in range(1, len(slices)):
            slices[s] = slices[s] + slices[s - 1]
        return modules, defaults, slices

    @classmethod
    def chk_mutex(cls, part_id, mod_cfg):
        """Check conflict in selections - Class Method

        Check if there is conflict in user selections ({mod_cfg}) of a
        specified part ({part_id})

        Args:
            part_id (int): An integer indicating the id number of a specified
                part from the hosts data file
            mod_cfg (int): A hex number indicating the config word of id
                selections for a specified part.

        Returns:
            A bool flag indicating whether there is a conflict or not.
            True : Conflict, False: No conflicts.
        """
        cls._cur.execute("SELECT mod_id, mutex FROM modules "
                "WHERE part_id=%s" % part_id)
        mutex_tuple = dict(cls._cur.fetchall())
        mutex_info = []
        mod_info = cls.get_ids(mod_cfg)
        for mod_id in mod_info:
            mutex_info.extend(cls.get_ids(mutex_tuple[mod_id]))
        mutex_info = set(mutex_info)
        for mod_id in mod_info:
            if mod_id in mutex_info:
                return False
        return True

    @classmethod
    def unpack(cls, packfile="hostslist.data", dbfile="hostslist.s3db"):
        """Unpack local data file - Class Method

        Unzip the zipped data file ({packfile}) to a SQLite database file
        ({dbfile}).
        """
        datafile = zipfile.ZipFile(packfile, "r")
        datafile.extract(dbfile)

    @classmethod
    def clear(cls):
        """Clear up workspace - Class Method

        Close the connection to the database and delete the database file.
        """
        cls._conn.close()
        os.remove(cls._database)

def make_hosts(cfgs, hostname):
    """Operations to make a hosts filename

    Make a new hosts file by data from the local data file.

    Args:
        cfgs (dict): A dictionary containing the hex config words for
            different parts of the data file.
        hostname (str): A string indicating the hostname of current operating
            system.
    """
    # Operations start
    start_time = time.time()
    hosts_file = open("hosts", "w")
    RetrieveData.unpack()
    RetrieveData.connect_db()
    # Fetches head section
    for head_str in RetrieveData.get_head():
        hosts_file.write("%s\n" % head_str[0])
    # Fetches info section
    info = RetrieveData.get_info()
    info_lines = ["#"]
    info_lines.append("# %s: %s" % ("Version", info["Version"]))
    info_lines.append("# %s: %s" % ("Buildtime", info["Buildtime"]))
    info_lines.append("# %s: %s" % ("Applytime", int(start_time)))
    info_lines.append("#")
    for line in info_lines:
        hosts_file.write("%s\n" % line)
    # Fetches hosts section
    for part_id in sorted(cfgs.keys()):
        mod_cfg = cfgs[part_id]
        if not RetrieveData.chk_mutex(part_id, mod_cfg):
            return
        mods = RetrieveData.get_ids(mod_cfg)
        if part_id == 0x02:
            # Retrieve localhost module
            for mod_id in mods:
                hosts, mod_name = RetrieveData.get_host(part_id, mod_id)
                hosts_file.write("\n# Section Start: %s\n" % mod_name)
                for host in hosts:
                    if hosts[1] == "#Replace Your Device Name Here!":
                        hosts[1] = hostname
                    hosts_file.write("%s %s\n" % (host[0], host[1]))
                hosts_file.write("# Section End: %s\n" % mod_name)
        else:
            # Retrieve common modules
            for mod_id in mods:
                hosts, mod_name = RetrieveData.get_host(part_id, mod_id)
                hosts_file.write("\n# Section Start: %s\n" % mod_name)
                for host in hosts:
                    hosts_file.write("%s %s\n" % (host[0], host[1]))
                hosts_file.write("# Section End: %s\n" % mod_name)
    hosts_file.close()
    RetrieveData.clear()
    # Operations end
    end_time = time.time()
    total_time = "%.4f" % (end_time - start_time)

if __name__ == "__main__":
    # Module Test
    selection = {0x02: 0x0001, 0x08: 0x0001, 0x10: 0x003F, 0x40: 0x000F}
    make_hosts(selection, "TEST-PC")
