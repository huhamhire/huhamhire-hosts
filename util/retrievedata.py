#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# retrievedata.py : Read data from the hosts data file
#
# Copyleft (C) 2014 - huhamhire hosts team <develop@huhamhire.com>
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
import sqlite3
import zipfile

DATAFILE = "./hostslist.data"
DATABASE = "./hostslist.s3db"


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
    def db_exists(cls, database=DATABASE):
        """Check if database exists - Class Method

        Check whether the database file exists or not.

        Args:
            database (str): A string indicating the SQLite database file.
                "hostslist.s3db" by default.

        Returns:
            A boolean indicating if the database file exists.
        """
        return os.path.isfile(database)

    @classmethod
    def connect_db(cls, database=DATABASE):
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
                         "WHERE part_id=%s AND mod_id = %s"
                         % (part_id, mod_id))
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
            cls._cur.execute('SELECT COUNT(mod_id) FROM modules '
                             'WHERE part_id=?', (ch_part, ))
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
    def unpack(cls, datafile=DATAFILE, database=DATABASE):
        """Unpack local data file - Class Method

        Unzip the zipped data file ({packfile}) to a SQLite database file
        ({dbfile}).
        """
        datafile = zipfile.ZipFile(datafile, "r")
        path, file = os.path.split(database)
        datafile.extract(file, path)

    @classmethod
    def clear(cls):
        """Clear up workspace - Class Method

        Close the connection to the database and delete the database file.
        """
        cls._conn.close()
        os.remove(cls._database)
