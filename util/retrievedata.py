#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# retrievedata.py : Retrieve data from the hosts data file.
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
import sqlite3
import zipfile

DATAFILE = "./hostslist.data"
DATABASE = "./hostslist.s3db"


class RetrieveData(object):
    """
    RetrieveData class contains a set of tools to retrieve information from
    the hosts data file.

    .. note:: All methods from this class are declared as `classmethod`.

    :ivar sqlite3.connect conn: An instance of :class:`sqlite3.connect`
        object to set up connection to a SQLite database.
    :ivar sqlite3.connect.cursor _cur: An instance of
        :class:`sqlite3.connect.cursor` object to process SQL queries in the
        database.
    :ivar str _db: Filename of a SQLite database file.
    """
    conn = None
    _cur = None
    _database = None

    @classmethod
    def db_exists(cls, database=DATABASE):
        """
        Check whether the :attr:`database` file exists or not.

        .. note:: This is a `classmethod`.

        :param database: Path to a SQLite database file.
                `./hostslist.s3db` by default.
        :type database: str
        :return: A flag indicating whether the database file exists or not.
        :rtype: bool
        """
        return os.path.isfile(database)

    @classmethod
    def connect_db(cls, database=DATABASE):
        """
        Set up connection with a SQLite :attr:`database`.

        .. note:: This is a `classmethod`.

        :param database: Path to a SQLite database file.
                `./hostslist.s3db` by default.
        :type database: str
        """
        cls.conn = sqlite3.connect(database)
        cls._cur = cls.conn.cursor()
        cls._database = database

    @classmethod
    def disconnect_db(cls):
        """
        Close the connection with a SQLite database.

        .. note:: This is a `classmethod`.
        """
        cls.conn.close()

    @classmethod
    def get_info(cls):
        """
        Retrieve the metadata of current data file.

        .. note:: This is a `classmethod`.

        :return: Metadata of current data file. The metadata here is a
            dictionary while the `Keys` are made of `Section Name` and
            `Values` are made of `Information` defined in the hosts data file.
        :rtype: dict
        """
        cls._cur.execute("SELECT sect, info FROM info;")
        info = dict(cls._cur.fetchall())
        return info

    @classmethod
    def get_head(cls):
        """
        Retrieve the head information from hosts data file.

        .. note:: This is a `classmethod`.

        :return: Lines of hosts head information.
        :rtype: list
        """
        cls._cur.execute("SELECT str FROM hosts_head ORDER BY ln;")
        head = cls._cur.fetchall()
        return head

    @classmethod
    def get_ids(cls, id_cfg):
        """
        Calculate the id numbers covered by config word :attr:`id_cfg`.

        .. note:: This is a `classmethod`.

        :param id_cfg: A hexadecimal config word of id selections.
        :type id_cfg: int
        :return: ID numbers covered by config word.
        :rtype: list
        """
        cfg = bin(id_cfg)[:1:-1]
        ids = []
        for i, id_en in enumerate(cfg):
            if int(id_en):
                ids.append(0b1 << i)
        return ids

    @classmethod
    def get_host(cls, part_id, mod_id):
        """
        Retrieve the hosts module specified by :attr:`mod_id` from a part
        specified by :attr:`part_id` in the data file.

        .. note:: This is a `classmethod`.

        :param part_id: ID number of a specified part from the hosts data
            file.

            .. note:: ID number is usually an 8-bit control byte.
        :type part_id: int
        :param mod_id: ID number of a specified module from a specified part.

            .. note:: ID number is usually an 8-bit control byte.
        :type mod_id: int

        .. seealso:: :attr:`make_cfg` in
            :class:`~tui.curses_d.CursesDaemon` class.

        :return: hosts, mod_name

            * hosts(`list`): Hosts entries from a specified module.
            * mod_name(`str`): Name of a specified module.
        :rtype: list, str
        """
        if part_id == 0x04:
            return None, "customize"
        cls._cur.execute("""
            SELECT part_name FROM parts
            WHERE part_id=:part_id;
        """, (part_id, ))
        part_name = cls._cur.fetchone()[0]
        cls._cur.execute("""
            SELECT ip, host FROM %s
            WHERE cate=%s;
        """ % (part_name, mod_id))
        hosts = cls._cur.fetchall()
        cls._cur.execute("""
            SELECT mod_name FROM modules
            WHERE part_id=:part_id AND mod_id=:mod_id;
        """, (part_id, mod_id))
        mod_name = cls._cur.fetchone()[0]
        return hosts, mod_name

    @classmethod
    def get_choice(cls, flag_v6=False):
        """
        Retrieve module selection items from the hosts data file with default
        selection for users.

        .. note:: This is a `classmethod`.

        :param flag_v6: A flag indicating whether to receive IPv6 hosts
            entries or the IPv4 ones. Default by `False`.

                ===============  =======
                :attr:`flag_v6`  hosts
                ===============  =======
                True             IPv6
                False            IPv4
                ===============  =======
        :type flag_v6: bool
        :return: modules, defaults, slices

            * modules(`list`): Information of modules for users to select.
            * defaults(`dict`): Default selection config for selected parts.
            * slices(`list`): Numbers of modules in each part.
        :rtype: list, dict, list
        """
        ch_parts = (0x08, 0x20 if flag_v6 else 0x10, 0x40)
        cls._cur.execute("""
            SELECT * FROM modules
            WHERE part_id IN (:id_shared, :id_ipv, :id_adblock);
        """, ch_parts)
        modules = cls._cur.fetchall()
        cls._cur.execute("""
            SELECT part_id, part_default FROM parts
            WHERE part_id IN (:id_shared, :id_ipv, :id_adblock);
        """, ch_parts)
        default_cfg = cls._cur.fetchall()
        defaults = {}
        for default in default_cfg:
            defaults[default[0]] = cls.get_ids(default[1])
        slices = [0]
        for ch_part in ch_parts:
            cls._cur.execute("""
                SELECT COUNT(mod_id) FROM modules
                WHERE part_id=:ch_part;
            """, (ch_part, ))
            slices.append(cls._cur.fetchone()[0])
        for s in range(1, len(slices)):
            slices[s] += slices[s - 1]
        return modules, defaults, slices

    @classmethod
    def chk_mutex(cls, part_id, mod_cfg):
        """
        Check if there is conflict in user selections :attr:`mod_cfg` from a
        part specified by :attr:`part_id` in the data file.

        .. note:: A conflict may happen while one module selected is declared
            in `mutex` word of ano module selected at the same time.

        .. note:: This is a `classmethod`.

        :param part_id: ID number of a specified part from the hosts data
            file.

            .. note:: ID number is usually an 8-bit control byte.

            .. seealso:: :meth:`~util.retrievedata.get_host`.

        :type part_id: int
        :param mod_cfg: A 16-bit config word indicating module selections of a
            specified part.

            .. note::
                If modules in specified part whose IDs are `0x0002` and
                `0x0010`, the value here should be `0x0002 + 0x0010 = 0x0012`,
                which is `0b0000000000000010 + 0b0000000000010000 =
                0b0000000000010010` in binary.

        :type: int

        .. seealso:: :attr:`make_cfg` in
            :class:`~tui.curses_d.CursesDaemon` class.

        :return: A flag indicating whether there is a conflict or not.

            ======  ============
            Return  Status
            ======  ============
            True    Conflict
            False   No conflicts
            ======  ============

        :rtype: bool
        """
        if part_id == 0x04:
            return True
        cls._cur.execute("""
            SELECT mod_id, mutex FROM modules
            WHERE part_id=:part_id;
        """, (part_id, ))
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
        """
        Unzip the archived :attr:`datafile` to a SQLite database file
        :attr:`database`.

        .. note:: This is a `classmethod`.

        :param datafile: Path to the zipped data file. `./hostslist.data` by
            default.
        :type datafile: str
        :param database: Path to a SQLite database file. `./hostslist.s3db` by
            default.
        :type database: str
        """
        datafile = zipfile.ZipFile(datafile, "r")
        path, filename = os.path.split(database)
        datafile.extract(filename, path)

    @classmethod
    def clear(cls):
        """
        Close connection to the database and delete the database file.

        .. note:: This is a `classmethod`.
        """
        cls.conn.close()
        os.remove(cls._database)
