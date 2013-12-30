#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from source_data import SourceData


class DomainListData(QObject):
    get_new_id_signal = SIGNAL("GetNewID")

    def __init__(self, parent=None):
        super(DomainListData, self).__init__(parent)
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
        return [result["domain"] for result in self._domain_results]

    @pyqtSlot(str)
    def get_domain_id(self, domain):
        for result in self._domain_results:
            if result["domain"] == str(domain):
                self.emit(self.get_new_id_signal, int(result["id"]))


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
    select_new_signal = SIGNAL("SelectNewItem(QString)")

    def __init__(self, parent):
        super(DomainListView, self).__init__(parent)

    def selectionChanged(self, selected, deselected):
        item = selected[0].indexes()[0].data().toString()
        self.emit(self.select_new_signal, item)
        super(DomainListView, self).selectionChanged(selected, deselected)


class DomainListFilter(QLineEdit):
    def __init__(self, model, parent=None):
        super(DomainListFilter, self).__init__(parent)
        self._data_model = model
        self.textChanged.connect(self.update_filter)
        self.setPlaceholderText("Filter")

    def update_filter(self):
        reg_text = self.text()
        if len(reg_text.split(" ")) > 1:
            reg_ex = reg_text.split(" ").join("([A-Za-z0-9]*[.-_]*)+")
        else:
            reg_ex = QStringList(list(reg_text)).join("([A-Za-z0-9]*[.-_]*)+")
        self._data_model.setFilterRegExp(reg_ex)


class DomainListWidget(QWidget):
    set_new_test_table_signal = SIGNAL("SetNewTestTable")

    def __init__(self, *args):
        QWidget.__init__(self, *args)

        list_data = DomainListData(self)
        list_view = DomainListView(self)

        list_view.connect(
            list_view, list_view.select_new_signal,
            list_data.get_domain_id
        )
        list_data.connect(
            list_data, list_data.get_new_id_signal, self.set_new_test_table
        )

        proxy_model = DomainListProxyModel(list_view)

        list_data.set_module_tag("ipv4-google")
        data = list_data.domain_list()

        list_model = DomainListModel(data, self)

        proxy_model.setSourceModel(list_model)
        proxy_model.setDynamicSortFilter(True)

        list_filter = DomainListFilter(proxy_model, self)
        list_view.setModel(proxy_model)

        layout = QVBoxLayout(self)
        layout.setMargin(5)
        layout.addWidget(list_filter)
        layout.addWidget(list_view)
        self.setLayout(layout)

    @pyqtSlot(long)
    def set_new_test_table(self, domain_id):
        self.emit(self.set_new_test_table_signal, domain_id)


class TestWidget(QWidget):
    def __init__(self, *args):
        super(TestWidget, self).__init__(*args)
        self.resize(1024, 640)

        from DomainTestModel import DomainTestWidget

        domain_list = DomainListWidget()
        test_table = DomainTestWidget()

        domain_list.connect(
            domain_list, domain_list.set_new_test_table_signal,
            test_table.set_table_data
        )

        splitter = QSplitter(self)
        splitter.resize(1024, 640)
        splitter.addWidget(domain_list)
        splitter.setStretchFactor(0, 1)
        splitter.addWidget(test_table)
        splitter.setStretchFactor(1, 4)
        splitter.setHandleWidth(3)

        layout = QHBoxLayout(self)
        layout.addWidget(splitter)

        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    w = TestWidget()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()