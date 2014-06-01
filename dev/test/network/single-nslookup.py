#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from dev.network.Nslookup import MultiNSLookup
from dev.progress import ProgressWidget


def main():
    app = QApplication(sys.argv)
    w = ProgressWidget()
    w.show()

    thread = TestNSLookup(w)
    thread.start()

    sys.exit(app.exec_())


class TestNSLookup(QThread):
    def __init__(self, parent):
        super(TestNSLookup, self).__init__(parent)
        self.logger = parent.logger

    def run(self):
        self.test_nslookup()

    def test_nslookup(self):
        ns_servers = {
            "us": "64.118.80.141",
            "uk": "62.24.228.202",
            "de": "37.221.193.195",
            "fr": "82.216.111.121",
            "ru": "62.16.86.100",

            "cn-u": "221.12.1.227",
            "cn-t": "114.114.114.114",

            "hk": "202.181.224.2",
            "tw": "168.95.192.1",
            "jp": "61.199.193.162",
            "sg": "165.21.83.88",
            "kr": "164.124.101.46",
            "in": "58.68.121.230",
        }

        filters = {"share-apple": ["cn-t"]}
        domains = {"share-apple": ["blog.huhamhire.com"]}
        v6 = True

        lookups = MultiNSLookup(ns_servers, filters, domains, self.logger, v6)
        responses = lookups.nslookup()

        print(responses)


if __name__ == '__main__':
    main()