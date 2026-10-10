# -*- coding: utf-8 -*-
"""
Symbol Card — Custom QFrame that displays a symbol character + Chinese name.

Click to copy the symbol to clipboard. Emits symbol_copied signal.
Supports flash animation on copy success.
"""
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QMenu, QAction,
                              QApplication)


class SymbolCard(QFrame):
    """A card widget showing one symbol with its Chinese name."""

    # Emitted when this symbol is successfully copied
    symbol_copied = pyqtSignal(dict)

    # Emitted when card is clicked (for focus tracking)
    card_clicked = pyqtSignal(object)

    CARD_WIDTH = 96
    CARD_HEIGHT = 96
    CHAR_FONT_SIZE = 26
    NAME_FONT_SIZE = 10

    def __init__(self, symbol_data, parent=None):
        """
        Args:
            symbol_data: dict with keys 'char', 'name', 'unicode'
        """
        super().__init__(parent)
        self._symbol = symbol_data

        self.setProperty('class', 'symbol-card')
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setToolTip(
            f"{symbol_data['char']} — {symbol_data['name']}\n"
            f"Unicode: {symbol_data['unicode']}\n"
            f"点击复制符号 · 右键更多选项"
        )

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 8, 4, 6)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        # Symbol character label
        self._char_label = QLabel(symbol_data['char'])
        self._char_label.setProperty('class', 'symbol-char')
        self._char_label.setAlignment(Qt.AlignCenter)
        char_font = QFont()
        char_font.setPixelSize(self.CHAR_FONT_SIZE)
        self._char_label.setFont(char_font)
        layout.addWidget(self._char_label)

        # Symbol name label
        self._name_label = QLabel(symbol_data['name'])
        self._name_label.setProperty('class', 'symbol-name')
        self._name_label.setAlignment(Qt.AlignCenter)
        self._name_label.setWordWrap(True)
        self._name_label.setMaximumHeight(28)
        name_font = QFont()
        name_font.setPixelSize(self.NAME_FONT_SIZE)
        self._name_label.setFont(name_font)
        layout.addWidget(self._name_label)

        # Copy flash timer
        self._flash_timer = QTimer(self)
        self._flash_timer.setSingleShot(True)
        self._flash_timer.timeout.connect(self._reset_style)

    def symbol_data(self):
        """Return the symbol dict for this card."""
        return self._symbol

    def mousePressEvent(self, event):
        """Left click → copy symbol. Right click → context menu."""
        if event.button() == Qt.LeftButton:
            self.card_clicked.emit(self)
            self._copy_to_clipboard()
        elif event.button() == Qt.RightButton:
            self._show_context_menu(event.globalPos())

    def contextMenuEvent(self, event):
        """Right-click context menu."""
        self._show_context_menu(event.globalPos())

    def keyPressEvent(self, event):
        """Enter/Space → copy symbol."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self._copy_to_clipboard()
        else:
            super().keyPressEvent(event)

    def _show_context_menu(self, pos):
        """Show right-click menu with copy options."""
        menu = QMenu(self)

        copy_action = QAction(f"复制符号: {self._symbol['char']}", menu)
        copy_action.triggered.connect(self._copy_to_clipboard)
        menu.addAction(copy_action)

        copy_unicode = QAction(f"复制 Unicode: {self._symbol['unicode']}", menu)
        copy_unicode.triggered.connect(self._copy_unicode)
        menu.addAction(copy_unicode)

        copy_name = QAction(f"复制名称: {self._symbol['name']}", menu)
        copy_name.triggered.connect(self._copy_name)
        menu.addAction(copy_name)

        menu.exec_(pos)

    def _copy_to_clipboard(self):
        """Copy the symbol character to clipboard."""
        text = self._symbol['char']
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self._flash_copied()
        self.symbol_copied.emit(self._symbol)

    def _copy_unicode(self):
        """Copy the Unicode code point to clipboard."""
        QApplication.clipboard().setText(self._symbol['unicode'])

    def _copy_name(self):
        """Copy the Chinese name to clipboard."""
        QApplication.clipboard().setText(self._symbol['name'])

    def _flash_copied(self):
        """Brief green flash to indicate successful copy."""
        self.setStyleSheet(
            f".symbol-card {{"
            f"  background-color: rgba(52, 211, 153, 0.15);"
            f"  border: 1px solid #34d399;"
            f"  border-radius: 12px;"
            f"}}"
        )
        self._flash_timer.start(300)

    def _reset_style(self):
        """Reset card style after flash."""
        self.setStyleSheet('')
