# -*- coding: utf-8 -*-
"""
Search Bar — QLineEdit subclass with built-in debounce timer.

Emits search_requested(str) signal after user stops typing for 150ms.
Also handles Escape key to clear search.
"""
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QLineEdit


class SearchBar(QLineEdit):
    """Search input with debounced text change notifications."""

    # Emitted after debounce period with the current search text
    search_requested = pyqtSignal(str)

    # Emitted immediately when Escape is pressed or text cleared
    search_cleared = pyqtSignal()

    DEBOUNCE_MS = 150

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('searchBar')
        self.setProperty('class', 'search-bar')
        self.setPlaceholderText('🔍  搜索符号名称...')
        self.setClearButtonEnabled(True)
        self.setMinimumHeight(36)

        # Debounce timer
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._emit_search)

        # Track last emitted query to avoid duplicate signals
        self._last_query = ''

        # Connect text changes
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text):
        """Handle text input — restart debounce timer."""
        stripped = text.strip()
        if stripped == self._last_query:
            return

        # If cleared, emit immediately
        if not stripped and self._last_query:
            self._last_query = ''
            self._debounce_timer.stop()
            self.search_cleared.emit()
            return

        # Restart debounce
        self._debounce_timer.stop()
        self._debounce_timer.start(self.DEBOUNCE_MS)

    def _emit_search(self):
        """Emit search_requested with current (debounced) query."""
        query = self.text().strip()
        if query != self._last_query:
            self._last_query = query
            self.search_requested.emit(query)

    def keyPressEvent(self, event):
        """Handle Escape to clear search."""
        if event.key() == Qt.Key_Escape:
            if self.text():
                self.clear()
                self.search_cleared.emit()
                return
        super().keyPressEvent(event)

    def clear_search(self):
        """Clear the search field programmatically."""
        self._last_query = ''
        self._debounce_timer.stop()
        self.clear()
