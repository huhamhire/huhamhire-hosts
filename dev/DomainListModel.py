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

        if not SourceData.is_connected:
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

    def __init__(self, parent=None):
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
        super(DomainListWidget, self).__init__(*args)

        self._list_data = DomainListData(self)
        self._list_view = DomainListView(self)

        self._list_view.connect(
            self._list_view,
            self._list_view.select_new_signal,
            self._list_data.get_domain_id
        )
        self._list_data.connect(
            self._list_data,
            self._list_data.get_new_id_signal,
            self.set_new_test_table
        )

        data = self._list_data.domain_list()
        self._list_model = DomainListModel(data, self)

        self._proxy_model = DomainListProxyModel(self._list_view)
        self._proxy_model.setSourceModel(self._list_model)
        self._proxy_model.setDynamicSortFilter(True)

        self._list_filter = DomainListFilter(self._proxy_model, self)
        self._list_view.setModel(self._proxy_model)

        self.setTabOrder(self._list_filter, self._list_view)

        layout = QVBoxLayout(self)
        layout.setMargin(5)
        layout.addWidget(self._list_filter)
        layout.addWidget(self._list_view)
        self.setLayout(layout)

    @pyqtSlot(long)
    def set_new_test_table(self, domain_id):
        self.emit(self.set_new_test_table_signal, domain_id)

    @pyqtSlot(QString)
    def set_new_domain_list(self, domain_label):
        tag = str(domain_label)
        self._list_data.set_module_tag(tag)
        data = self._list_data.domain_list()
        self._list_model = DomainListModel(data, self)
        self._proxy_model.reset()
        self._proxy_model.setSourceModel(self._list_model)
        self._list_filter.setText("")

        if self._list_view.model().rowCount():
            item = self._list_view.model().index(0, 0)
            self._list_view.setCurrentIndex(item)
        else:
            self.emit(self.set_new_test_table_signal, None)


def main():
    app = QApplication(sys.argv)
    w = DomainListWidget()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()