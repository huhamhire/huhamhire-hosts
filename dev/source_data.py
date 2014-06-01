#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  source_data.py
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
    is_connected = False

    @staticmethod
    def __calc_id(in_string):
        identity = hashlib.md5(in_string).hexdigest()[:8]
        return int(identity, 16)

    @classmethod
    def connect_db(cls, database="test.s3db"):
        cls._conn = sqlite3.connect(database)
        cls._cur = cls._conn.cursor()
        cls._db = database
        cls.is_connected = True

    @classmethod
    def disconnect_db(cls):
        cls._cur.close()
        cls.is_connected = False

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
    def __set_domain(cls, domain, module):
        ins_sql = "REPLACE INTO t_domain VALUES (" \
                  ":domain_id, :name, NULL, :mod)"
        domain_id = cls.__calc_id(domain)
        data = (domain_id, domain, module)
        try:
            cls._cur.execute(ins_sql, data)
        except sqlite3.IntegrityError, e:
            sys.stderr.write(str(e) + "\n")

    @classmethod
    def set_multi_domain_list(cls, domains, module):
        for domain in domains:
            cls.__set_domain(domain, module)
        cls._conn.commit()

    @classmethod
    def set_single_domain(cls, domain, module):
        cls.__set_domain(domain, module)
        cls._conn.commit()

    @classmethod
    def __set_ns_response(cls, domain, multi_responses):
        for server_tag, response in multi_responses.iteritems():
            # Update status info
            status = response["stat"]
            domain_id = cls.__calc_id(domain)
            upd_sql = "UPDATE t_domain SET stat=:stat " \
                      "WHERE id=:id AND stat>:stat"
            data = {"stat": status,
                    "id": domain_id,
                    }
            try:
                cls._cur.execute(upd_sql, data)
            except sqlite3.IntegrityError, e:
                sys.stderr.write(str(e) + "\n")

            for ip in response["hosts"]:
                ip_id = cls.__calc_id(ip)
                ins_sql = "INSERT OR IGNORE INTO t_ip VALUES (:ip_id, :ip);"
                try:
                    cls._cur.execute(ins_sql, (ip_id, ip))
                except sqlite3.IntegrityError, e:
                    sys.stderr.write(str(e) + "\n")

                comb_id = cls.__calc_id(domain + ip)

                ins_sql = "INSERT OR IGNORE INTO t_domain_ip VALUES (" \
                          ":domain, :ip, :comb, '');"
                upd_sql = "UPDATE t_domain_ip SET ns=ns||:ns " \
                          "WHERE domain_id=:domain AND ip_id=:ip;"
                data = {
                    "domain": domain_id,
                    "ip": ip_id,
                    "comb": comb_id,
                    "ns": server_tag + '|'
                }
                try:
                    cls._cur.execute(ins_sql, data)
                    cls._cur.execute(upd_sql, data)
                except sqlite3.IntegrityError, e:
                    sys.stderr.write(str(e) + "\n")

    @classmethod
    def set_multi_ns_response(cls, ns_responses):
        for domain, response in ns_responses.iteritems():
            cls.__set_ns_response(domain, response)
        cls._conn.commit()

    @classmethod
    def set_single_ns_response(cls, domain, response):
        cls.__set_ns_response(domain, response)
        cls._conn.commit()

    @classmethod
    def __set_http_test(cls, ip_id, response):
        methods = ["http", "https"]
        count = response["req_count"]
        for method in methods:
            if method in response.keys():
                stat = response[method]
                ssl_flag = methods.index(method)
                ins_sql = "REPLACE INTO t_httpTest VALUES (" \
                          "  :ip_id, :ssl_flag, :min_delay, :max_delay, " \
                          "  :avg_delay, :ratio, :status, :test_count);"
                data = (ip_id, ssl_flag, stat["delay"]["min"],
                        stat["delay"]["max"], stat["delay"]["avg"],
                        stat["delay"]["ratio"], stat["status"], count)
                try:
                    cls._cur.execute(ins_sql, data)
                except sqlite3.IntegrityError, e:
                    sys.stderr.write(str(e) + "\n")

    @classmethod
    def set_multi_http_test_dict(cls, http_responses):
        for ip_id, response in http_responses.iteritems():
            cls.__set_http_test(ip_id, response)
        cls._conn.commit()

    @classmethod
    def set_single_http_test(cls, ip_id, response):
        cls.__set_ns_response(ip_id, response)
        cls._conn.commit()

    @classmethod
    def __set_ping_test(cls, ip_id, response):
        ins_sql = "REPLACE INTO t_pingTest VALUES (" \
                  ":ip_id, :min, :max, :avg, :ratio, :count);"
        data = (ip_id, response["min"], response["max"], response["avg"],
                response["ratio"], response["ping_count"])
        try:
            cls._cur.execute(ins_sql, data)
        except sqlite3.IntegrityError, e:
            sys.stderr.write(str(e) + "\n")

    @classmethod
    def set_multi_ping_test_dict(cls, ping_responses):
        for ip_id, response in ping_responses.iteritems():
            cls.__set_ping_test(ip_id, response)
        cls._conn.commit()

    @classmethod
    def set_single_ping_test(cls, ip_id, response):
        cls.__set_ping_test(ip_id, response)
        cls._conn.commit()

    @classmethod
    def clear(cls):
        cls._cur.execute("VACUUM")

    @classmethod
    def get_domain_list(cls):
        sql = "SELECT name, mod FROM t_domain;"
        cls._cur.execute(sql)
        domains = {}
        sql_results = cls._cur.fetchmany(1000)
        while sql_results:
            for result in sql_results:
                mod_name = result[1].encode("ascii")
                domain = result[0].encode("ascii")
                if mod_name in domains:
                    domains[mod_name].append(domain)
                else:
                    domains[mod_name] = [domain]
            sql_results = cls._cur.fetchmany(1000)
        return domains

    @classmethod
    def get_http_test_comb(cls):
        sql = "SELECT DISTINCT " \
              "  name AS domain, ip, ip_id AS id " \
              "FROM " \
              "  t_domain " \
              "  LEFT JOIN t_domain_ip " \
              "    ON t_domain.id = t_domain_ip.domain_id " \
              "  LEFT JOIN t_ip " \
              "    ON t_domain_ip.ip_id = t_ip.id " \
              "WHERE " \
              "  ip IS NOT NULL " \
              "GROUP BY " \
              "  ip " \
              "ORDER BY" \
              "  id;"
        cls._cur.execute(sql)
        tests = []
        sql_results = cls._cur.fetchmany(1000)
        while sql_results:
            for result in sql_results:
                item = dict(zip(["domain", "ip", "id"], list(result)))
                tests.append(item)
            sql_results = cls._cur.fetchmany(1000)
        return tests

    @classmethod
    def get_http_test_extend_comb(cls):
        sql = "SELECT " \
              "  name AS domain, ip, combination_id AS id " \
              "FROM " \
              "  t_domain " \
              "  LEFT JOIN t_domain_ip " \
              "    ON t_domain.id = t_domain_ip.domain_id " \
              "  LEFT JOIN t_ip " \
              "    ON t_domain_ip.ip_id = t_ip.id " \
              "WHERE " \
              "  ip IS NOT NULL;"
        cls._cur.execute(sql)
        tests = []
        sql_results = cls._cur.fetchmany(1000)
        while sql_results:
            for result in sql_results:
                item = dict(zip(["domain", "ip", "id"], list(result)))
                tests.append(item)
            sql_results = cls._cur.fetchmany(1000)
        return tests

    @classmethod
    def get_ping_test_comb(cls):
        sql = "SELECT ip, id FROM t_ip ORDER BY id;"
        cls._cur.execute(sql)
        tests = []
        sql_results = cls._cur.fetchmany(1000)
        while sql_results:
            for result in sql_results:
                item = dict(zip(["ip", "ip_id"], list(result)))
                tests.append(item)
            sql_results = cls._cur.fetchmany(1000)
        return tests

    @classmethod
    def get_ping_results_by_domain_id(cls, domain_id):
        sql = "SELECT t_domain_ip.ip_id AS ip_id, " \
              "  t_ip.ip AS ip," \
              "  t_pingTest.min_delay AS ping_min," \
              "  t_pingTest.max_delay AS ping_max," \
              "  t_pingTest.avg_delay AS ping_avg," \
              "  t_pingTest.ratio AS ping_ratio," \
              "  t_pingTest.test_count AS test_count," \
              "  t_domain_ip.ns AS ns " \
              "FROM t_domain_ip" \
              "  LEFT JOIN t_ip ON t_domain_ip.ip_id = t_ip.id" \
              "  LEFT JOIN t_pingTest ON " \
              "    t_domain_ip.ip_id = t_pingTest.ip_id " \
              "WHERE " \
              "  t_domain_ip.domain_id=:domain_id;"
        data = (domain_id, )
        cls._cur.execute(sql, data)
        results = []
        sql_results = cls._cur.fetchall()
        for result in sql_results:
            item = dict(zip(
                ["id", "ip", "min", "max", "avg", "ratio", "count", "ns"],
                list(result))
            )
            results.append(item)
        return results

    @classmethod
    def get_http_results_by_domain_id(cls, domain_id):
        sql = "SELECT t_domain_ip.ip_id AS ip_id," \
              "  t_ip.ip AS ip," \
              "  t_httpTest.ssl_flag AS ssl_flag," \
              "  t_httpTest.min_delay AS http_min," \
              "  t_httpTest.max_delay AS http_max," \
              "  t_httpTest.avg_delay AS http_avg," \
              "  t_httpTest.ratio AS http_ratio," \
              "  t_httpTest.test_count AS test_count," \
              "  t_httpTest.status AS status," \
              "  t_domain_ip.ns AS ns " \
              "FROM t_domain_ip" \
              "  LEFT JOIN t_ip ON t_domain_ip.ip_id = t_ip.id" \
              "  LEFT JOIN t_httpTest ON " \
              "    t_domain_ip.ip_id = t_httpTest.ip_id " \
              "WHERE t_domain_ip.domain_id=:domain_id;"
        data = (domain_id, )
        cls._cur.execute(sql, data)
        results = []
        sql_results = cls._cur.fetchall()
        for result in sql_results:
            item = dict(zip(
                ["id", "ip", "ssl", "min", "max", "avg", "ratio",
                 "count", "status", "ns"],
                list(result))
            )
            results.append(item)
        return results

    @classmethod
    def get_domains_by_module_tag(cls, tag):
        sql = "SELECT id, name FROM t_domain WHERE mod like :tag;"
        data = (tag + "%", )
        cls._cur.execute(sql, data)
        results = []
        sql_results = cls._cur.fetchall()
        for result in sql_results:
            item = dict(zip(
                ["id", "domain"], list(result)
            ))
            results.append(item)
        return results

    @classmethod
    def get_domain_modules(cls):
        sql = "SELECT DISTINCT mod FROM t_domain;"
        cls._cur.execute(sql)
        results = []
        sql_results = cls._cur.fetchall()
        for result in sql_results:
            results.append(result[0])
        return results


if __name__ == "__main__":
    SourceData.connect_db()
    SourceData.get_http_test_comb()
