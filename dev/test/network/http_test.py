#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from dev.source_data import SourceData
from dev.network import MultiHttpTest
from dev.progress import ProgressWidget


def main():
    app = QApplication(sys.argv)
    w = ProgressWidget()
    w.show()

    thread = TestHttp(w)
    thread.start()

    sys.exit(app.exec_())


class TestHttp(QThread):
    def __init__(self, parent):
        super(TestHttp, self).__init__(parent)
        self.logger = parent.logger

    def run(self):
        self.test_http()

    def test_http(self):
        SourceData.connect_db("../../test.s3db")
        combs = SourceData.get_http_test_comb()
        ext_combs = SourceData.get_http_test_extend_comb()

        http_tests = MultiHttpTest(combs, ext_combs, self.logger)
        results = http_tests.http_test()

        SourceData.set_multi_http_test_dict(results)


if __name__ == '__main__':
    main()