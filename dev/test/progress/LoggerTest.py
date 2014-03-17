#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from dev.progress import ProgressWidget


def main():
    app = QApplication(sys.argv)
    w = ProgressWidget()
    w.show()

    thread = TestText(w)
    thread.start()

    sys.exit(app.exec_())


class TestText(QThread):
    def __init__(self, parent):
        super(TestText, self).__init__(parent)
        self.logger = parent.logger

    def run(self):
        self.test_text()

    def test_text(self):
        logger = self.logger
        logger.log_err(["error"])
        logger.log_ok(["ok"])
        logger.log_normal(["normal"])
        for i in range(20):
            logger.log_normal(["=" * 80])
            time.sleep(0.2)


if __name__ == "__main__":
    main()
