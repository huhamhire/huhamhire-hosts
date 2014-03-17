#!/usr/bin/env python
# -*- coding: utf-8 -*

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from dev.source_data import SourceData
from dev.network import MultiPingTest
from dev.progress import ProgressWidget


def main():
    app = QApplication(sys.argv)
    w = ProgressWidget()
    w.show()

    thread = TestPing(w)
    thread.start()

    sys.exit(app.exec_())


class TestPing(QThread):
    def __init__(self, parent):
        super(TestPing, self).__init__(parent)
        self.logger = parent.logger

    def run(self):
        self.test_ping()

    def test_ping(self):
        SourceData.connect_db("../../test.s3db")
        combs = SourceData.get_ping_test_comb()

        ping_tests = MultiPingTest(combs, self.logger)
        results = ping_tests.ping_test()

        SourceData.set_multi_ping_test_dict(results)


if __name__ == '__main__':
    main()