#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4.QtGui import *


class CheckWidget(QWidget):
    def __init__(self, *args):
        super(CheckWidget, self).__init__(*args)
        self.resize(1280, 640)

        from ModuleTreeModel import ModuleTreeWidget
        from DomainListModel import DomainListWidget
        from DomainTestTableModel import DomainTestTableWidget

        module_tree = ModuleTreeWidget()
        domain_list = DomainListWidget()
        domain_test_table = DomainTestTableWidget()

        module_tree.connect(
            module_tree,
            module_tree.set_new_module_signal,
            domain_list.set_new_domain_list
        )
        domain_list.connect(
            domain_list,
            domain_list.set_new_test_table_signal,
            domain_test_table.set_table_data
        )

        splitter = QSplitter(self)
        splitter.resize(1024, 640)
        splitter.addWidget(module_tree)
        splitter.setStretchFactor(0, 1)
        splitter.addWidget(domain_list)
        splitter.setStretchFactor(1, 1)
        splitter.addWidget(domain_test_table)
        splitter.setStretchFactor(2, 4)
        splitter.setHandleWidth(3)

        layout = QHBoxLayout(self)
        layout.addWidget(splitter)

        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    w = CheckWidget()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()