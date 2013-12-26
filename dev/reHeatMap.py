#!/usr/bin/env python
# -*- coding: utf-8 -*-

import heatmap
import sqlite3


class ReHeatMap(object):
    def heatmap(self):
        sql = "SELECT t_httpTest.avg_delay AS http_avg, " \
              "  t_pingTest.avg_delay AS ping_avg " \
              "FROM t_domain " \
              "  LEFT JOIN t_domain_ip ON t_domain.id = t_domain_ip.domain_id " \
              "  LEFT JOIN t_ip ON t_domain_ip.ip_id = t_ip.id " \
              "  LEFT JOIN t_pingTest ON t_domain_ip.ip_id = t_pingTest.ip_id " \
              "  LEFT JOIN t_httpTest ON t_domain_ip.combination_id = t_httpTest.http_id;"
        conn = sqlite3.connect("test.s3db")
        cur = conn.cursor()
        cur.execute(sql)
        results = cur.fetchall()
        pts = []
        for http, ping in results:
            if http == None or http > 10000:
                continue
            if ping == None or ping > 600:
                continue
            pts.append((int(http), int(ping)))
        hm = heatmap.Heatmap()
        hm.heatmap(pts, dotsize=200, opacity=196,
                   size=(10000, 10000), scheme="classic",
                   area=((0, 0), (10000, 600))
        ).save("test.png")


if __name__ == "__main__":
    rec = ReHeatMap()
    rec.heatmap()
