#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4.QtGui import *

from dev.logger import LoggerWidget

def main():
    app = QApplication(sys.argv)
    w = LoggerWidget()
    test_text(w)
    w.show()
    sys.exit(app.exec_())


def test_text(logger_widget):
    logger_view = logger_widget.logger_view
    logger_view.append_error_message("error")
    logger_view.append_okay_message("ok")
    logger_view.append_normal_message("normal")
    for i in range(1000):
        logger_view.append_okay_message("=" * 80)


if __name__ == "__main__":
    main()