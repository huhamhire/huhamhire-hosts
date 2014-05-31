#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from source_data import SourceData


class CheckWidget(QWidget):
    def __init__(self, *args):
        super(CheckWidget, self).__init__(*args)
        self.resize(1280, 640)

        if not SourceData.is_connected:
            SourceData.connect_db()

        from ModuleTreeModel import ModuleTreeWidget
        from DomainListModel import DomainListWidget
        from DomainTestTableModel import DomainTestTabWidget

        module_tree = ModuleTreeWidget()
        domain_list = DomainListWidget()

        test_tab = DomainTestTabWidget(self)

        module_tree.connect(
            module_tree,
            module_tree.set_new_module_signal,
            domain_list.set_new_domain_list
        )
        domain_list.connect(
            domain_list,
            domain_list.set_new_test_table_signal,
            test_tab.update_table_data_by_domain
        )

        splitter = QSplitter(self)
        splitter.resize(1024, 640)
        splitter.addWidget(module_tree)
        splitter.setStretchFactor(0, 1)
        splitter.addWidget(domain_list)
        splitter.setStretchFactor(1, 1)
        splitter.addWidget(test_tab)
        splitter.setStretchFactor(2, 4)
        splitter.setHandleWidth(3)

        self.setTabOrder(module_tree, domain_list)
        self.setTabOrder(domain_list, test_tab)

        layout = QHBoxLayout(self)
        layout.setMargin(10)
        layout.addWidget(splitter)

        self.setLayout(layout)
        module_tree.set_default()

    def __del__(self):
        if SourceData.is_connected:
            SourceData.disconnect_db()


def main():
    app = QApplication(sys.argv)
    with open("./theme/dracula.qss", "r") as qss:
        app.setStyleSheet(qss.read())
    w = CheckWidget()
    # w.setWindowFlags(Qt.FramelessWindowHint)
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()