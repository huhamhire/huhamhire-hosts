#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from source_data import SourceData


class DomainListData(object):
    def __init__(self):
        self.__module_tag = None
        self._domain_results = []
        SourceData.connect_db()

    def set_module_tag(self, tag):
        self.__module_tag = tag
        self.get_domain_list()

    def get_domain_list(self):
        if self.__module_tag is not None:
            self._domain_results = SourceData.get_domains_by_module_tag(
                self.__module_tag
            )

    def domain_list(self):
        return [item["domain"] for item in self._domain_results]


class DomainListProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(DomainListProxyModel, self).__init__(parent)

    def filterAcceptsRow(self, src_row, src_parent):
        if self.filterRegExp() == QRegExp(u''):
            return True
        src_index = self.sourceModel().index(src_row, 0)
        item = src_index.data(Qt.DisplayRole).toString()
        return item.contains(self.filterRegExp())


class DomainListModel(QAbstractListModel):
    def __init__(self, list_data, parent=None):
        """ list_data: a list where each item is a row
        """
        QAbstractListModel.__init__(self, parent)
        self.__list_data = list_data

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.__list_data)

    def data(self, index, role=None):
        if index.isValid() and role == Qt.DisplayRole:
            return QVariant(self.__list_data[index.row()])
        else:
            return QVariant()


class DomainListView(QListView):

    def __init__(self, parent):
        super(DomainListView, self).__init__(parent)

    def selectionChanged(self, selected, deselected):
        self.emit(SIGNAL('newDomainSelection'))
        print selected[0].indexes()[0].data().toString()
        super(DomainListView, self).selectionChanged(selected, deselected)


class DomainListFilter(QLineEdit):
    def __init__(self, model, parent=None):
        super(DomainListFilter, self).__init__(parent)
        self._data_model = model
        self.textChanged.connect(self.update_filter)

    def update_filter(self):
        reg_text = self.text()
        if len(reg_text.split(" ")) > 1:
            reg_ex = reg_text.split(" ").join("[A-Za-z0-9]*[.-_]*")
        else:
            reg_ex = QStringList(list(reg_text)).join("[A-Za-z0-9]*[.-_]*")
        self._data_model.setFilterRegExp(reg_ex)


class MyWindow(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.resize(320, 640)

        list_data = DomainListData()
        list_view = DomainListView(self)
        proxy_model = DomainListProxyModel(list_view)

        list_data.set_module_tag("ipv4-google")
        data = list_data.domain_list()

        list_model = DomainListModel(data, self)

        proxy_model.setSourceModel(list_model)
        proxy_model.setDynamicSortFilter(True)

        list_filter = DomainListFilter(proxy_model, self)
        list_view.setModel(proxy_model)

        layout = QVBoxLayout()
        layout.addWidget(list_filter)
        layout.addWidget(list_view)
        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()