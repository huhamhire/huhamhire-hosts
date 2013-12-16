#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  data.py
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

__author__ = "huhamhire <me@huhamhire.com>"

import hashlib
import sqlite3
import sys


class SourceData(object):
    _conn = None
    _cur = None
    _db = ""

    @staticmethod
    def __calc_id(in_string):
        identity = hashlib.md5(in_string).hexdigest()[:8]
        return int(identity, 16)

    @classmethod
    def connect_db(cls, db="test.s3db"):
        cls._conn = sqlite3.connect(db)
        cls._cur = cls._conn.cursor()
        cls._db = db

    @classmethod
    def create_tables(cls):
        with open("./schema.sql", "r") as script:
            for sql in script.read().split(";"):
                cls._cur.execute(sql)

    @classmethod
    def drop_tables(cls):
        with open("./clear.sql", "r") as script:
            for sql in script.read().split(";"):
                cls._cur.execute(sql)

    @classmethod
    def __insert_domain(cls, domain, response):
        status = response["stat"]
        ins_sql = "INSERT INTO t_domain VALUES (:domain_id, :name, :stat)"
        domain_id = cls.__calc_id(domain)
        data = (domain_id, domain, status)
        try:
            cls._cur.execute(ins_sql, data)
        except sqlite3.IntegrityError, e:
            sys.stdout.write(str(e) + "\n")

        for ip in response["hosts"]:
            ip_id = cls.__calc_id(ip)
            ins_sql = "INSERT INTO t_ip VALUES (:ip_id, :ip)"
            try:
                cls._cur.execute(ins_sql, (ip_id, ip))
            except sqlite3.IntegrityError, e:
                if "column id is not unique" not in e:
                    sys.stdout.write(str(e) + "\n")

            ins_sql = "INSERT INTO t_domain_ip VALUES (:domain_id, :ip_id)"
            try:
                cls._cur.execute(ins_sql, (domain_id, ip_id))
            except sqlite3.IntegrityError, e:
                sys.stdout.write(str(e) + "\n")

    @classmethod
    def insert_multi_domain_dict(cls, ns_responses):
        for domain, response in ns_responses.iteritems():
            cls.__insert_domain(domain, response)
        cls._conn.commit()

    @classmethod
    def insert_single_domain(cls, domain, response):
        cls.__insert_domain(domain, response)
        cls._conn.commit()


if __name__ == "__main__":
    SourceData.connect_db()
    SourceData.drop_tables()
    SourceData.create_tables()