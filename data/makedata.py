#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  makedata.py : Tools to make hosts datafile for huhamhire-hosts
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

__version__ = '1.0.1'
__revision__ = "$Id$"
__author__ = "huhamhire <me@huhamhire.com>"

__all__ = [ 'MakeData', 'get_mod_info', 'make' ]

import hashlib
import json
import os
import sqlite3
import time
import zipfile
from xml.etree.ElementTree import ElementTree

# File Settings
DATA_PATH = "../../release/data/"
DATA_NAME = "hostslist.data"
DATA_FILE = DATA_PATH + DATA_NAME
JSON_FILE = DATA_PATH + "hostsinfo.json"
MOD_EXTENSION = ".hosts"

class MakeData(object):
    """A class to creat data file for huhamhire-hosts

    MakeData class contains a set of tools to creat the data file for clients
    of huhamhire-hosts. Including methods to retrieve data from module file
    and store the data into a SQLite database.

    Attributes:
        _conn (obj): A sqlite3.connect object indicating the connection to
            the SQLite database.
        _cur (obj): A sqlite3.connect.cursor object indicating the connection
            cursor with the SQLite database.
        _database (str): A string indicating the SQLite database file.
            "hosts.s3db" by default.
        count (int): An integer used to count the total number of hosts
            entries inserted into the database.
    """
    _conn = None
    _cur = None
    _database = None
    count = 0

    @classmethod
    def connect_db(cls, database="hostslist.s3db"):
        """Connect to database - Class Method

        Set up connection with a SQLite database.

        Args:
            database (str): A string indicating the SQLite database file.
                "hostslist.s3db" by default.
        """
        if os.path.exists(database):
            os.remove(database)
        cls._conn = sqlite3.connect(database)
        cls._cur = cls._conn.cursor()
        cls._database = database

    @classmethod
    def create_table(cls, table, mode="hosts"):
        """Creat data table - Class Method

        Creat a table ({tble}) in the database.

        Args:
            table (str): A string indicating the name of the table to be
                created
            mode (str): A string indicating the mode to creat the data table.
                "hosts" by default.
        """
        table_sqls = {
            "hosts": """CREATE TABLE %s (
                id UNSIGNED INTEGER PRIMARY KEY NOT NULL,
                cate SMALLINT, ip VARCHAR(40), host TEXT)""" % table,
            "head": """CREATE TABLE %s (
                ln UNSIGNED INTEGER PRIMARY KEY NOT NULL, str TEXT)"""% table,
            "info": """CREATE TABLE %s (
                sect VARCHAR(20) PRIMARY KEY NOT NULL, info TEXT)""" % table,
            "modules": """CREATE TABLE %s (
                part_id INTEGER, mod_id INTEGER, mutex INTEGER,
                mod_name VARCHAR(20),
                CONSTRAINT p_key PRIMARY KEY (part_id, mod_id))""" % table,
            "parts": """CREATE TABLE %s (
                part_id INTEGER PRIMARY KEY NOT NULL, part_default INTEGER,
                part_name VARCHAR(20))""" % table,
            }
        cls._cur.execute(table_sqls[mode])

    @classmethod
    def insert_host(cls, table, module, category):
        """Insert hosts entries = Class Method

        Fetch hosts data from a specified module file ({module}), and store
        the entries with their category id ({category}) in a specified
        table ({table}).

        Args:
            table (str): A string indicating the name of a table to insert
                data into.
            module (str): A string indicating the path of module file
                containing localhost data.
            category (int): An integer indicating the category of a specified
                module.
        """
        instream = open(module, 'rU')
        lines = instream.readlines()
        for line in lines:
            if line.startswith('#'):
                continue
            items = line.split()
            if len(items) < 2:
                continue
            index = hashlib.md5(items[0] + items[1]).hexdigest()[:8]
            index = int(index, 16)
            host = (index, category, items[0], items[1])
            try:
                insert_sql = "INSERT INTO %s VALUES (?, ?, ?, ?)" % table
                cls._cur.execute(insert_sql, host)
                cls.count += 1
            except sqlite3.IntegrityError:
                pass
        instream.close()

    @classmethod
    def insert_localhost(cls, table, module, platform):
        """Insert localhost entries = Class Method

        Fetch localhost data from a specified module file ({module}), and
        store the entries with their platform id ({platform}) in a specified
        table ({table}).

        Args:
            table (str): A string indicating the name of a table to insert
                data into.
            module (str): A string indicating the path of module file
                containing localhost data.
            platform (int): An integer indicating the platform of a specified
                module.
        """
        instream = open(module, 'rU')
        lines = instream.readlines()
        for line in lines:
            if line.startswith('#'):
                continue
            items = line.split()
            if len(items) < 2:
                continue
            if len(items) > 2:
                items[1] = ' '.join(items[1:])
                items = items[:2]
            index = hashlib.md5(str(cls.count)).hexdigest()[:8]
            index = int(index, 16)
            host = (index, platform, items[0], items[1])
            try:
                insert_sql = "INSERT INTO %s VALUES (?, ?, ?, ?)" % table
                cls._cur.execute(insert_sql, host)
                cls.count += 1
            except sqlite3.IntegrityError:
                pass
        instream.close()

    @classmethod
    def insert_head(cls, table, module):
        """Insert head entries = Class Method

        Fetch head lines from a specified module file ({module}), and store
        them in a specified table ({table}).

        Args:
            table (str): A string indicating the name of a table to insert
                data into.
            module (str): A string indicating the path of module file
                containing head data.
        """
        instream = open(module, 'rU')
        lines = instream.readlines()
        insert_sql = "INSERT INTO %s VALUES (?, ?)" % table
        for ln, line in enumerate(lines):
            if not line.startswith('#'):
                continue
            line = line[:-1]
            cls._cur.execute(insert_sql, (ln, line))
        instream.close()

    @classmethod
    def insert_info(cls, table, field, info):
        """Insert information entries = Class Method

        Store the information ({info}) of a specified entry with the field
        name ({field}) into a specified table ({table}).

        Args:
            table (str): A string indicating the name of a table to insert
                data into.
            field (str): A string indicating the field name of a specified
                entry.
            info (str): A string indicating the information of a specified
                entry.
        """
        insert_sql = "INSERT INTO %s VALUES (?, ?)" % table
        cls._cur.execute(insert_sql, (field, info))

    @classmethod
    def insert_moduleinfo(cls, table, part):
        """Insert module information - Class Method

        Store the information of a module ({part}) into a specified
        table ({table}).

        Args:
            table (str): A string indicating the name of a table to insert
                data into.
            part (dict): A dictionary containing the information of a
                specified module.
        """
        insert_sql = "INSERT INTO %s VALUES (?, ?, ?, ?)" % table
        for mod in part["modules"]:
            mod_info = (part["part_id"], mod["category"], mod["mutex"],
                        mod["name"])
            cls._cur.execute(insert_sql, mod_info)

    @classmethod
    def insert_partinfo(cls, table, part):
        """Insert part information - Class Method

        Store the information of a data partition ({part}) into a specified
        table ({table}).

        Args:
            table (str): A string indicating the name of a table to insert
                data into.
            part (dict): A dictionary containing the information of a
                specified partition.
        """
        insert_sql = "INSERT INTO %s VALUES (?, ?, ?)" % table
        part_info = (part["part_id"], part["default"], part["table"])
        cls._cur.execute(insert_sql, part_info)

    @classmethod
    def packtozip(cls, packfile):
        """Pack up datafile - Class Method

        Add the database file to an archive file ({packfile}).

        Args:
            packfile (str): A string indicating the file name of the data
                package.
        """
        cls._conn.commit()
        pack = zipfile.ZipFile(packfile, 'w', zipfile.ZIP_DEFLATED)
        pack.write(cls._database, cls._database)
        pack.close()

    @classmethod
    def clear(cls):
        """Clear up workspace - Class Method

        Close the connection to the database and delete the database file.
        """
        cls._conn.close()
        os.remove(cls._database)


class MakeJSON(object):
    """A class to creat info-file of data-file for huhamhire-hosts

    MakeJSON class contains a set of tools to creat the json file to describe
    the data file for huhamhire-hosts. Including methods to calculate the MD5
    checksum and SHA1 checksum of the data-file.
    """
    @classmethod
    def _calc_md5(cls, filepath):
        """Calculate MD5 Checksum - Class Method

        Calculate MD5 checksum of the data-file.

        Args:
            filepath (str): A string indicating the path of the data-file.

        Returns:
            A MD5 checksum string.
        """
        with open(filepath,'rb') as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            hash = md5obj.hexdigest()
            return hash

    @classmethod
    def _calc_sha1(cls, filepath):
        """Calculate SHA1 Checksum - Class Method

        Calculate SHA1 checksum of the data-file.

        Args:
            filepath (str): A string indicating the path of the data-file.

        Returns:
            A SHA1 checksum string.
        """
        with open(filepath,'rb') as f:
            sha1obj = hashlib.sha1()
            sha1obj.update(f.read())
            hash = sha1obj.hexdigest()
            return hash

    @classmethod
    def _get_filesize(cls, filepath):
        """Check file size - Class Method

        Get the file size of the data-file.

        Args:
            filepath (str): A string indicating the path of the data-file.

        Returns:
            An integer indicating the size(bytes) of the data-file.
        """
        return os.path.getsize(filepath)

    @classmethod
    def makejson(cls, filepath, version):
        """Make the JSON file - Class Method

        Creat info-file of data-file for huhamhire-hosts.

        Args:
            filepath (str): A string indicating the path of data-file.
            version (str): A string indicating the version of data-file.
        """
        global DATA_NAME, JSON_FILE
        fileinfo = {
            "filename": DATA_NAME,
            "version": version,
            "md5": cls._calc_md5(filepath),
            "sha1": cls._calc_sha1(filepath),
            "size": cls._get_filesize(filepath),
        }
        print "Filesize: %d" % fileinfo["size"]
        print "MD5: %s" % fileinfo["md5"]
        print "SHA1: %s" % fileinfo["sha1"]
        j_str = json.dumps(fileinfo)
        j_file = open(JSON_FILE, "w")
        j_file.write(j_str)
        j_file.close()


def get_mod_info(infile="mods.xml"):
    """Fetches information of hosts mudules

    Retrieves module information from a xml file ({infile}).

    Returns:
        A tuple contains a partition info list, a head info dictionary and a
        database info dictionary.
    """
    tree = ElementTree()
    xmlfile = tree.parse(infile)
    version = xmlfile.get("version")
    # Get partition information
    parts = []
    for xml_part in xmlfile.iter(tag='part'):
        part_info= {}
        part_info["part_id"] = int(xml_part.get("id"), 16)
        part_info["default"] = int(xml_part.get("default"), 16)
        part_info["table"] = xml_part.find("table").text
        part_info["modpath"] = xml_part.find("path").text
        mods = xml_part.find("modules")
        modules = []
        for mod in mods:
            mod_info = {}
            mod_info["category"] = int(mod.get("cate"), 16)
            mod_info["mutex"] = int(mod.get("mutex"), 16)
            mod_info["name"] = mod.text
            modules.append(mod_info)
        part_info["modules"] = modules
        parts.append(part_info)
    # Get head information
    head = {}
    xml_head = xmlfile.find("head")
    head["part_id"] = int(xml_head.get("id"), 16)
    head["default"] = int(xml_part.get("default"), 16)
    head["table"] = xml_head.find("table").text
    head["modpath"] = xml_head.find("path").text
    head["module"] = xml_head.find("module").text
    # Get database information
    info = {}
    xml_info = xmlfile.find("info")
    info["part_id"] = int(xml_info.get("id"), 16)
    info["default"] = int(xml_part.get("default"), 16)
    info["table"] = xml_info.find("table").text
    return parts, head, info, version

def make():
    """Make data file

    Operations to make a hosts datafile which contains all latest hosts
    entries.
    """
    parts, head, info, version = get_mod_info()
    mod_extension = MOD_EXTENSION
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)
    # Operations start
    start_time = time.time()
    MakeData.connect_db()
    MakeData.create_table("modules", "modules")
    MakeData.create_table("parts", "parts")
    # Insert hosts data
    insert_func = [MakeData.insert_host, MakeData.insert_localhost]
    for part in parts:
        MakeData.insert_moduleinfo("modules", part)
        MakeData.insert_partinfo("parts", part)
        MakeData.create_table(part["table"])
        local = part["table"] == "localhost"
        for mod in part["modules"]:
            mod_file = ''.join([part["modpath"], mod["name"], mod_extension])
            print "Applying %s" % mod_file
            insert_func[local](part["table"], mod_file, mod["category"])
    MakeData.create_table(head["table"], "head")
    head_file = ''.join([head["modpath"], head["module"], mod_extension])
    MakeData.insert_head(head["table"], head_file)
    MakeData.insert_partinfo("parts", head)
    # Insert information data
    timestamp = str(int(start_time))
    MakeData.create_table(info["table"], "info")
    MakeData.insert_info(info["table"], "Buildtime", timestamp)
    MakeData.insert_info(info["table"], "Author", __author__)
    MakeData.insert_info(info["table"], "Version", version)
    MakeData.insert_partinfo("parts", info)
    global DATA_FILE
    MakeData.packtozip(DATA_FILE)
    MakeData.clear()
    # Operations end
    end_time = time.time()
    total_time = "%.4f" % (end_time - start_time)
    print "%d entries inserted in %ss." % (MakeData.count, total_time)
    print '-' * 60
    MakeJSON.makejson(DATA_FILE, version)

if __name__ == "__main__":
    make()
