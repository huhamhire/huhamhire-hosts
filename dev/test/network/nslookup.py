#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from dev.set_domain import SetDomain
from dev.source_data import SourceData
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
            "us": "4.2.2.1",
            "uk": "62.24.228.202",
            "de": "37.221.193.195",
            "fr": "213.251.133.164",
            "ru": "62.16.86.100",

            "cn-u": "221.12.1.227",
            "cn-t": "114.114.114.114",

            "hk": "202.181.224.2",
            "tw": "168.95.192.1",
            "jp": "218.223.68.1",
            "sg": "202.136.162.11",
            "kr": "168.126.63.1",
            "in": "58.68.121.230",
        }
        cfg_path = "../../modules/"
        cfg_file = "modules.xml"
        database = "../../test.s3db"
        set_domain = SetDomain(cfg_path, cfg_file, database)
        set_domain.get_config()
        set_domain.get_domains_in_mods()
        filters = set_domain.get_ns_filters()
        domains = SourceData.get_domain_list()

        lookups = MultiNSLookup(ns_servers, filters, domains, self.logger)
        responses = lookups.nslookup()

        SourceData.set_multi_ns_response(responses)


if __name__ == '__main__':
    main()