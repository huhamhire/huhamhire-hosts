#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from source_data import SourceData


class ModuleTreeData(QObject):

    def __init__(self, parent=None):
        super(ModuleTreeData, self).__init__(parent)
        if not SourceData.is_connected:
            SourceData.connect_db()
        self.__modules = SourceData.get_domain_modules()
        self.__tree = []
        self.make_tree()

    def recursive_make_tree(self, root, part_mod):
        delimiter = "-"
        parts = part_mod.split(delimiter, 1)
        item_idx = -1
        for i, item in enumerate(root):
            if item[0][0] == parts[0]:
                item_idx = i
                break
        if item_idx >= 0:
            if len(parts) > 1:
                self.recursive_make_tree(root[item_idx][1], parts[1])
        else:
            if len(parts) > 1:
                child_nodes = []
                self.recursive_make_tree(child_nodes, parts[1])
                root.append(((parts[0], ), child_nodes))
            else:
                root.append(((parts[0], ), []))

    def make_tree(self):
        for mod in self.__modules:
            self.recursive_make_tree(self.__tree, mod)

    def module_tree_data(self):
        return self.__tree


class ModuleTreeItem(QObject):
    def __init__(self, data, parent_item=None, parent=None):
        super(ModuleTreeItem, self).__init__(parent)
        self.parent_item = parent_item
        self.item_data = data
        self.child_items = []

    def append_child(self, item):
        self.child_items.append(item)

    def child(self, row):
        return self.child_items[row]

    def child_count(self):
        return len(self.child_items)

    def column_count(self):
        return len(self.item_data)

    def data(self, column):
        try:
            return self.item_data[column]
        except IndexError:
            return None

    def parent(self):
        return self.parent_item

    def row(self):
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0


class ModuleTreeModel(QAbstractItemModel):
    def __init__(self, data, parent=None):
        super(ModuleTreeModel, self).__init__(parent)

        self.root_item = ModuleTreeItem(("Modules", ))
        self.recursive_set_model_data(data, self.root_item)

    def columnCount(self, parent=None, *args, **kwargs):
        if parent.isValid():
            return parent.internalPointer().column_count()
        else:
            return self.root_item.column_count()

    def data(self, index, role=None):
        if not index.isValid():
            return None
        if role != Qt.DisplayRole:
            return None
        item = index.internalPointer()
        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.root_item.data(section)
        return None

    def index(self, row, column, parent=None, *args, **kwargs):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def parent(self, index=None):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent=None, *args, **kwargs):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        return parent_item.child_count()

    def recursive_set_model_data(self, data, root):
        for node in data:
            item = ModuleTreeItem(node[0], root)
            if len(node[1]) > 0:
                self.recursive_set_model_data(node[1], item)
            root.append_child(item)


class ModuleTreeProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(ModuleTreeProxyModel, self).__init__(parent)

    def filterAcceptsRow(self, src_row, src_parent):
        if self.filterRegExp() == QRegExp(u''):
            return True
        src_index = self.sourceModel().index(src_row, 0, src_parent)
        if self.sourceModel().hasChildren(src_index):
            return self.filter_accepts_row_children(src_index) or \
                self.filter_accepts_row_self(src_index)
        else:
            return self.filter_accepts_row_self(src_index)

    def filter_accepts_row_children(self, parent_index):
        for row in range(self.sourceModel().rowCount(parent_index)):
            src_index = self.sourceModel().index(row, 0, parent_index)
            if self.filter_accepts_row_self(src_index) or (
                self.sourceModel().hasChildren(src_index) and
                self.filter_accepts_row_children(src_index)
            ):
                return True
        return False

    def filter_accepts_row_self(self, src_index):
        item = src_index.data(Qt.DisplayRole).toString()
        return item.contains(self.filterRegExp())


class ModuleTreeFilter(QLineEdit):
    def __init__(self, model, tree_view, parent=None):
        super(ModuleTreeFilter, self).__init__(parent)
        self._data_model = model
        self._tree_view = tree_view
        self.textChanged.connect(self.update_filter)
        self.setPlaceholderText("Filter")

    def update_filter(self):
        reg_text = self.text()
        if len(reg_text.split(" ")) > 1:
            reg_ex = reg_text.split(" ").join("([A-Za-z0-9]*[.-_]*)+")
        else:
            reg_ex = QStringList(list(reg_text)).join("([A-Za-z0-9]*[.-_]*)+")
        self._data_model.setFilterRegExp(reg_ex)
        self._tree_view.expandAll()


class ModuleTreeView(QTreeView):
    select_new_signal = SIGNAL("SelectNewItem(QString)")

    def __init__(self, parent=None):
        super(ModuleTreeView, self).__init__(parent)

    def selectionChanged(self, selected, deselected):
        item = selected[0].indexes()[0]
        tags = []
        while True:
            item_tag = item.data().toString()
            if not item_tag:
                break
            tags.append(item_tag)
            item = item.parent()
        tags.reverse()
        label = QStringList(tags).join("-")

        self.emit(self.select_new_signal, label)
        super(ModuleTreeView, self).selectionChanged(selected, deselected)


class ModuleTreeWidget(QWidget):
    set_new_module_signal = SIGNAL("SetNewModule(QString)")

    def __init__(self, *args):
        super(ModuleTreeWidget, self).__init__(*args)

        self._tree_data = ModuleTreeData(self)
        self._tree_model = ModuleTreeModel(
            self._tree_data.module_tree_data(), self
        )
        self._tree_view = ModuleTreeView(self)

        self._tree_view.connect(
            self._tree_view,
            self._tree_view.select_new_signal,
            self.set_new_module
        )

        self._proxy_model = ModuleTreeProxyModel(self._tree_view)
        self._proxy_model.setSourceModel(self._tree_model)

        self._tree_view.setModel(self._proxy_model)
        self._tree_view.setHeaderHidden(True)
        self._tree_view.expandAll()

        self._tree_filter = ModuleTreeFilter(
            self._proxy_model, self._tree_view, self
        )

        self.setTabOrder(self._tree_filter, self._tree_view)

        layout = QVBoxLayout(self)
        layout.setMargin(2)
        layout.addWidget(self._tree_filter)
        layout.addWidget(self._tree_view)

        self.setLayout(layout)

    def set_default(self):
        if self._tree_view.model().rowCount():
            item = self._tree_view.model().index(0, 0)
            self._tree_view.setCurrentIndex(item)
            self.emit(self.set_new_module_signal, item.data().toString())
        else:
            self.emit(self.set_new_module_signal, None)

    @pyqtSlot(QString)
    def set_new_module(self, module_label):
        self.emit(self.set_new_module_signal, module_label)


def main():
    app = QApplication(sys.argv)
    w = ModuleTreeWidget()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
