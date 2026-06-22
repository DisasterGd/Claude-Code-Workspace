# -*- coding: utf-8 -*-
"""
Symbol Grid — Scrollable grid area with FlowLayout for symbol cards.

Supports:
    - Dynamic card rendering from symbol list
    - Responsive column count (cards reflow on resize)
    - Keyboard navigation (arrow keys within grid)
    - Focus management
"""
from PyQt5.QtCore import Qt, QSize, QRect, QPoint
from PyQt5.QtWidgets import (QScrollArea, QWidget, QLayout, QLayoutItem,
                              QWidgetItem, QStyle, QSizePolicy, QLabel,
                              QVBoxLayout)


# ═══════════════════════════════════════════════════════════════════════════
#  FlowLayout — Custom layout that wraps widgets like CSS flex-wrap
#  Based on the classic Qt FlowLayout example
# ═══════════════════════════════════════════════════════════════════════════

class FlowLayout(QLayout):
    """A layout that arranges child widgets left-to-right, top-to-bottom,
    wrapping to the next row when the available width is exceeded."""

    def __init__(self, parent=None, margin=0, spacing_h=-1, spacing_v=-1):
        super().__init__(parent)
        self._items = []
        self._h_spacing = spacing_h
        self._v_spacing = spacing_v
        self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        """Clean up items on destruction."""
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        """Add a QLayoutItem to the layout."""
        self._items.append(item)

    def horizontalSpacing(self):
        """Return horizontal spacing between items."""
        if self._h_spacing >= 0:
            return self._h_spacing
        return self._smart_spacing(QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        """Return vertical spacing between rows."""
        if self._v_spacing >= 0:
            return self._v_spacing
        return self._smart_spacing(QStyle.PM_LayoutVerticalSpacing)

    def count(self):
        """Return number of items."""
        return len(self._items)

    def itemAt(self, index):
        """Return item at index, or None."""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        """Remove and return item at index."""
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        """This layout grows only vertically."""
        return Qt.Orientations(Qt.Vertical)

    def hasHeightForWidth(self):
        """Height depends on width (for flow/wrapping)."""
        return True

    def heightForWidth(self, width):
        """Calculate required height for given width."""
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        """Arrange items in the given rectangle."""
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        """Preferred size based on all items."""
        return self.minimumSize()

    def minimumSize(self):
        """Calculate minimum size needed."""
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(),
                       margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect, test_only=False):
        """Core layout algorithm: arrange items in rows, wrapping at rect width.

        Returns the total height used (or required).
        """
        margins = self.contentsMargins()
        effective_rect = rect.adjusted(+margins.left(), +margins.top(),
                                        -margins.right(), -margins.bottom())
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0
        h_space = self.horizontalSpacing()
        v_space = self.verticalSpacing()

        for item in self._items:
            widget = item.widget()
            if widget and widget.isHidden():
                continue

            item_size = item.sizeHint()
            next_x = x + item_size.width() + h_space

            if next_x - h_space > effective_rect.right() and line_height > 0:
                # Wrap to next row
                x = effective_rect.x()
                y = y + line_height + v_space
                next_x = x + item_size.width() + h_space
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item_size))

            x = next_x
            line_height = max(line_height, item_size.height())

        total_height = y + line_height - rect.y() + margins.bottom()
        return total_height

    def _smart_spacing(self, pm):
        """Get default spacing from style."""
        parent = self.parentWidget()
        if parent:
            return parent.style().pixelMetric(pm, None, parent)
        return -1

    def clear(self):
        """Remove all items from layout."""
        while self.count():
            item = self.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


# ═══════════════════════════════════════════════════════════════════════════
#  SymbolGrid — Scrollable container with FlowLayout of SymbolCards
# ═══════════════════════════════════════════════════════════════════════════

class SymbolGrid(QScrollArea):
    """A scrollable grid of symbol cards using FlowLayout."""

    # Emitted when a symbol is copied
    symbol_copied = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setFrameShape(QScrollArea.NoFrame)

        # Container widget
        self._container = QWidget()
        self._container.setObjectName('gridContainer')
        self._layout = FlowLayout(self._container, margin=4, spacing_h=8, spacing_v=8)
        self.setWidget(self._container)

        # Track cards for keyboard navigation
        self._cards = []
        self._focused_index = -1

    def set_symbols(self, symbols):
        """Populate the grid with a list of symbol dicts.

        Args:
            symbols: list of dicts with 'char', 'name', 'unicode'
        """
        self._clear_grid()
        self._cards = []

        for sym in symbols:
            card = self._create_card(sym)
            self._layout.addWidget(card)
            self._cards.append(card)

        self._focused_index = -1
        # Ensure the container updates its geometry
        self._container.updateGeometry()

    def _create_card(self, symbol_data):
        """Create a SymbolCard and connect its signals."""
        # Avoid circular import
        from symbol_card import SymbolCard
        card = SymbolCard(symbol_data, self._container)
        card.symbol_copied.connect(self.symbol_copied.emit)
        card.card_clicked.connect(self._on_card_clicked)
        return card

    def _clear_grid(self):
        """Remove all cards from the grid."""
        self._layout.clear()
        self._cards = []

    def _on_card_clicked(self, card):
        """Track which card has focus for keyboard nav."""
        if card in self._cards:
            self._focused_index = self._cards.index(card)

    def current_cards(self):
        """Return list of currently displayed SymbolCard widgets."""
        return self._cards

    # ── Keyboard Navigation ────────────────────────────────────────────────

    def keyPressEvent(self, event):
        """Handle arrow keys for grid navigation."""
        key = event.key()
        card_count = len(self._cards)

        if card_count == 0:
            super().keyPressEvent(event)
            return

        if key in (Qt.Key_Right, Qt.Key_Down):
            self._focused_index = min(self._focused_index + 1, card_count - 1)
            self._focus_card(self._focused_index)
            return

        if key in (Qt.Key_Left, Qt.Key_Up):
            self._focused_index = max(self._focused_index - 1, 0)
            self._focus_card(self._focused_index)
            return

        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            if 0 <= self._focused_index < card_count:
                card = self._cards[self._focused_index]
                card._copy_to_clipboard()
            return

        if key == Qt.Key_Escape:
            # Let parent (main window) handle Escape
            super().keyPressEvent(event)
            return

        super().keyPressEvent(event)

    def _focus_card(self, index):
        """Set focus to card at given index and scroll to it."""
        if 0 <= index < len(self._cards):
            card = self._cards[index]
            card.setFocus()
            self.ensureWidgetVisible(card)

    def focus_first_card(self):
        """Focus the first card in the grid."""
        if self._cards:
            self._focused_index = 0
            self._cards[0].setFocus()

    def card_count(self):
        """Return number of cards currently displayed."""
        return len(self._cards)


# ═══════════════════════════════════════════════════════════════════════════
#  Empty State — placeholder shown when no results
# ═══════════════════════════════════════════════════════════════════════════

class EmptyState(QWidget):
    """Placeholder widget shown when there are no symbols to display."""

    def __init__(self, message='未找到匹配的符号', parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self._label = QLabel(message)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet('color: #94a3b8; font-size: 14px;')
        layout.addWidget(self._label)

        self._hint = QLabel('请尝试其他关键词')
        self._hint.setAlignment(Qt.AlignCenter)
        self._hint.setStyleSheet('color: #64748b; font-size: 12px;')
        layout.addWidget(self._hint)

    def set_message(self, message, hint=''):
        """Update the empty state message."""
        self._label.setText(message)
        if hint:
            self._hint.setText(hint)
            self._hint.show()
        else:
            self._hint.hide()
