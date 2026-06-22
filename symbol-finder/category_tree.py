# -*- coding: utf-8 -*-
"""
Category Tree — Left sidebar QTreeWidget showing category/subcategory hierarchy.

Two-level tree:
    Level 1 — Category (e.g., "常规标点", "货币符号")
    Level 2 — Subcategory (e.g., "破折号/连字符", "引号")

Emits subcategory_selected(category_id, subcategory_id) when user clicks a subcategory.
"""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QTreeWidget, QTreeWidgetItem, QHeaderView,
                              QVBoxLayout, QWidget, QLabel)

from symbol_data import CATEGORIES


class CategoryTree(QWidget):
    """Left sidebar widget containing category/subcategory tree."""

    # Emitted when user selects a subcategory
    subcategory_selected = pyqtSignal(str, str)  # category_id, subcategory_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('categorySidebar')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header label
        header = QLabel('分类')
        header.setStyleSheet(
            'font-size: 11px; font-weight: bold; color: #64748b; '
            'padding: 8px 12px 4px 12px; text-transform: uppercase; '
            'letter-spacing: 1px;'
        )
        layout.addWidget(header)

        # Tree widget
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(16)
        self._tree.setAnimated(True)
        self._tree.setExpandsOnDoubleClick(False)
        self._tree.setRootIsDecorated(True)
        self._tree.setFocusPolicy(Qt.StrongFocus)

        # Font setup
        font = QFont()
        font.setPixelSize(13)
        self._tree.setFont(font)

        layout.addWidget(self._tree)

        # Build the tree
        self._build_tree()

        # Connect signals
        self._tree.itemClicked.connect(self._on_item_clicked)
        self._tree.currentItemChanged.connect(self._on_current_changed)

        # Track previously expanded category for accordion behavior
        self._last_expanded_category = None

    def _build_tree(self):
        """Populate the tree with categories and subcategories from data."""
        for cat in CATEGORIES:
            cat_item = QTreeWidgetItem(self._tree)
            cat_item.setText(0, cat['name'])
            cat_item.setData(0, Qt.UserRole, {
                'type': 'category',
                'id': cat['id'],
            })
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemIsSelectable)

            # Subcategory count
            total = sum(len(sub['symbols']) for sub in cat['subcategories'])
            cat_item.setToolTip(0, f"{cat['name']} — {total} 个符号")

            bold_font = QFont()
            bold_font.setPixelSize(13)
            bold_font.setBold(True)
            cat_item.setFont(0, bold_font)

            for sub in cat['subcategories']:
                sub_item = QTreeWidgetItem(cat_item)
                count = len(sub['symbols'])
                sub_item.setText(0, f"{sub['name']} ({count})")
                sub_item.setData(0, Qt.UserRole, {
                    'type': 'subcategory',
                    'category_id': cat['id'],
                    'subcategory_id': sub['id'],
                })

            cat_item.setExpanded(True)

        # Default selection: first subcategory of first category
        if self._tree.topLevelItemCount() > 0:
            first_cat = self._tree.topLevelItem(0)
            if first_cat.childCount() > 0:
                first_sub = first_cat.child(0)
                self._tree.setCurrentItem(first_sub)

    def _on_item_clicked(self, item, column):
        """Handle click on tree item."""
        data = item.data(0, Qt.UserRole)
        if data is None:
            return

        if data['type'] == 'category':
            # Toggle expand/collapse
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
                # Select first subcategory if none selected under this category
                if item.childCount() > 0:
                    current = self._tree.currentItem()
                    if current is None or current.parent() != item:
                        self._tree.setCurrentItem(item.child(0))

        elif data['type'] == 'subcategory':
            self.subcategory_selected.emit(
                data['category_id'],
                data['subcategory_id']
            )

    def _on_current_changed(self, current, previous):
        """Handle selection change."""
        if current is None:
            return
        data = current.data(0, Qt.UserRole)
        if data and data['type'] == 'subcategory':
            self.subcategory_selected.emit(
                data['category_id'],
                data['subcategory_id']
            )

    def select_subcategory(self, category_id, subcategory_id):
        """Programmatically select a subcategory in the tree."""
        for i in range(self._tree.topLevelItemCount()):
            cat_item = self._tree.topLevelItem(i)
            cat_data = cat_item.data(0, Qt.UserRole)
            if cat_data and cat_data['id'] == category_id:
                cat_item.setExpanded(True)
                for j in range(cat_item.childCount()):
                    sub_item = cat_item.child(j)
                    sub_data = sub_item.data(0, Qt.UserRole)
                    if sub_data and sub_data['subcategory_id'] == subcategory_id:
                        self._tree.setCurrentItem(sub_item)
                        return

    def selected_subcategory(self):
        """Return (category_id, subcategory_id) of current selection, or None."""
        item = self._tree.currentItem()
        if item is None:
            return None
        data = item.data(0, Qt.UserRole)
        if data and data['type'] == 'subcategory':
            return (data['category_id'], data['subcategory_id'])
        return None

    def focus_tree(self):
        """Set keyboard focus to the tree."""
        self._tree.setFocus()
