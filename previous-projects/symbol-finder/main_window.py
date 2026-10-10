# -*- coding: utf-8 -*-
"""
Main Window — Central orchestrator combining all components.

Layout:
    ┌──────────────────────────────────────────────────┐
    │  Menu Bar: 文件  视图  帮助                        │
    ├──────────────────────────────────────────────────┤
    │  Title: Symbol Finder · 主题按钮                   │
    ├──────────────────┬───────────────────────────────┤
    │  Category Tree   │  Search Bar                    │
    │  (QSplitter)     │  Breadcrumb                    │
    │                  │  Symbol Grid                   │
    ├──────────────────┴───────────────────────────────┤
    │  Status Bar                                       │
    └──────────────────────────────────────────────────┘
"""
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QSplitter, QLabel, QPushButton, QMenuBar,
                              QMenu, QAction, QStatusBar, QApplication,
                              QShortcut)

from symbol_data import CATEGORIES, build_flat_index, get_total_symbol_count
from category_tree import CategoryTree
from search_bar import SearchBar
from symbol_grid import SymbolGrid
from theme_manager import load_theme, save_theme, apply_theme


class MainWindow(QMainWindow):
    """Main application window for Symbol Finder."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Symbol Finder — Windows 特殊符号查找工具')
        self.setMinimumSize(860, 600)
        self.resize(1100, 750)

        # ── State ──
        self._active_category_id = None
        self._active_subcategory_id = None
        self._is_searching = False
        self._search_results = []
        self._search_capped = False

        # Build flat search index
        self._all_symbols = build_flat_index()

        # ── Build UI ──
        self._setup_menu_bar()
        self._setup_central_widget()
        self._setup_status_bar()
        self._setup_shortcuts()

        # ── Initial State ──
        # The category_tree auto-selects the first subcategory,
        # which triggers subcategory_selected → _on_subcategory_selected
        self.status_bar.showMessage(
            f'共 {get_total_symbol_count()} 个符号 · 点击复制 · 方向键导航'
        )

    # ═══════════════════════════════════════════════════════════════════════
    #  Menu Bar
    # ═══════════════════════════════════════════════════════════════════════

    def _setup_menu_bar(self):
        menubar = self.menuBar()

        # ── File Menu ──
        file_menu = menubar.addMenu('文件(&F)')
        exit_action = QAction('退出(&Q)', self)
        exit_action.setShortcut(QKeySequence('Ctrl+Q'))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ── View Menu ──
        view_menu = menubar.addMenu('视图(&V)')
        self._theme_action = QAction('切换暗色/亮色主题(&T)', self)
        self._theme_action.setShortcut(QKeySequence('Ctrl+T'))
        self._theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(self._theme_action)

        view_menu.addSeparator()

        search_action = QAction('搜索符号(&S)', self)
        search_action.setShortcut(QKeySequence('Ctrl+F'))
        search_action.triggered.connect(self._focus_search)
        view_menu.addAction(search_action)

        # ── Help Menu ──
        help_menu = menubar.addMenu('帮助(&H)')
        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    # ═══════════════════════════════════════════════════════════════════════
    #  Central Widget & Layout
    # ═══════════════════════════════════════════════════════════════════════

    def _setup_central_widget(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Title Bar ──
        title_bar = QWidget()
        title_bar.setObjectName('titleBar')
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(16, 10, 16, 10)

        title_label = QLabel('Symbol Finder')
        title_label.setProperty('class', 'title-label')
        title_layout.addWidget(title_label)

        subtitle = QLabel('Windows 特殊符号查找工具')
        subtitle.setProperty('class', 'subtitle-label')
        title_layout.addWidget(subtitle)

        title_layout.addStretch()

        # Theme toggle button
        self._theme_btn = QPushButton()
        self._theme_btn.setProperty('class', 'theme-btn')
        self._theme_btn.setFixedSize(36, 32)
        self._theme_btn.setToolTip('切换暗色/亮色主题 (Ctrl+T)')
        self._theme_btn.clicked.connect(self._toggle_theme)
        self._update_theme_button()
        title_layout.addWidget(self._theme_btn)

        root_layout.addWidget(title_bar)

        # ── Splitter: Sidebar | Main Area ──
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)

        # Left: Category Tree
        self._category_tree = CategoryTree()
        self._category_tree.subcategory_selected.connect(
            self._on_subcategory_selected
        )
        splitter.addWidget(self._category_tree)

        # Right: Main content area
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(6)

        # Search bar
        self._search_bar = SearchBar()
        self._search_bar.search_requested.connect(self._on_search)
        self._search_bar.search_cleared.connect(self._on_search_cleared)
        right_layout.addWidget(self._search_bar)

        # Breadcrumb
        self._breadcrumb = QLabel()
        self._breadcrumb.setProperty('class', 'breadcrumb')
        right_layout.addWidget(self._breadcrumb)

        # Symbol grid
        self._symbol_grid = SymbolGrid()
        self._symbol_grid.symbol_copied.connect(self._on_symbol_copied)
        right_layout.addWidget(self._symbol_grid, stretch=1)

        splitter.addWidget(right_widget)

        # Set initial splitter ratio (260px sidebar : rest)
        splitter.setSizes([260, 840])
        splitter.setStretchFactor(0, 0)  # Sidebar fixed
        splitter.setStretchFactor(1, 1)  # Main area stretches

        root_layout.addWidget(splitter, stretch=1)

    # ═══════════════════════════════════════════════════════════════════════
    #  Status Bar
    # ═══════════════════════════════════════════════════════════════════════

    def _setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Status message with auto-clear timer
        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(self._reset_status)

    def _show_status(self, message, timeout=3000):
        """Show a temporary status message."""
        self.status_bar.showMessage(message)
        self._status_timer.stop()
        if timeout > 0:
            self._status_timer.start(timeout)

    def _reset_status(self):
        """Reset status bar to default message."""
        count = len(self._symbol_grid.current_cards())
        self.status_bar.showMessage(
            f'共 {count} 个符号 · 点击复制 · 方向键导航'
        )

    # ═══════════════════════════════════════════════════════════════════════
    #  Keyboard Shortcuts
    # ═══════════════════════════════════════════════════════════════════════

    def _setup_shortcuts(self):
        # Ctrl+F → focus search
        QShortcut(QKeySequence('Ctrl+F'), self, self._focus_search)

        # Ctrl+T → toggle theme
        QShortcut(QKeySequence('Ctrl+T'), self, self._toggle_theme)

        # Escape → handled by SearchBar.keyPressEvent to clear search

    # ═══════════════════════════════════════════════════════════════════════
    #  Theme
    # ═══════════════════════════════════════════════════════════════════════

    def _toggle_theme(self):
        """Toggle between dark and light theme."""
        app = QApplication.instance()
        new_theme = 'light' if load_theme() == 'dark' else 'dark'
        apply_theme(app, new_theme)
        save_theme(new_theme)
        self._update_theme_button()

    def _update_theme_button(self):
        """Update theme toggle button icon based on current theme."""
        current = load_theme()
        self._theme_btn.setText('☀️' if current == 'dark' else '🌙')

    # ═══════════════════════════════════════════════════════════════════════
    #  Category / Subcategory Handling
    # ═══════════════════════════════════════════════════════════════════════

    def _on_subcategory_selected(self, category_id, subcategory_id):
        """User clicked a subcategory in the tree → show its symbols."""
        self._is_searching = False
        self._search_bar.clear_search()
        self._active_category_id = category_id
        self._active_subcategory_id = subcategory_id

        # Find the subcategory data
        symbols = self._get_subcategory_symbols(category_id, subcategory_id)
        if symbols:
            self._symbol_grid.set_symbols(symbols)
            self._update_breadcrumb_for_browse(category_id, subcategory_id, len(symbols))
            self._symbol_grid.focus_first_card()

    def _get_subcategory_symbols(self, category_id, subcategory_id):
        """Get list of symbol dicts for a given subcategory."""
        for cat in CATEGORIES:
            if cat['id'] == category_id:
                for sub in cat['subcategories']:
                    if sub['id'] == subcategory_id:
                        return sub['symbols']
        return []

    def _update_breadcrumb_for_browse(self, category_id, subcategory_id, count):
        """Update breadcrumb for browse mode."""
        cat_name = ''
        sub_name = ''
        for cat in CATEGORIES:
            if cat['id'] == category_id:
                cat_name = cat['name']
                for sub in cat['subcategories']:
                    if sub['id'] == subcategory_id:
                        sub_name = sub['name']
                        break
                break
        self._breadcrumb.setText(f'{cat_name} > {sub_name} ({count} 个符号)')

    # ═══════════════════════════════════════════════════════════════════════
    #  Search Handling
    # ═══════════════════════════════════════════════════════════════════════

    def _on_search(self, query):
        """Perform search and display results."""
        if not query:
            return

        self._is_searching = True
        q = query.lower()

        # Filter all symbols by name
        results = [s for s in self._all_symbols if q in s['name'].lower()]

        self._search_capped = len(results) > 200
        if self._search_capped:
            self._search_results = results[:200]
        else:
            self._search_results = results

        # Update grid
        self._symbol_grid.set_symbols(self._search_results)

        # Update breadcrumb
        cap_hint = ' (显示前 200 个，请细化搜索)' if self._search_capped else ''
        self._breadcrumb.setText(
            f'搜索 "{query}" — {len(results)} 个结果{cap_hint}'
        )

        if self._search_results:
            self._symbol_grid.focus_first_card()

    def _on_search_cleared(self):
        """Search cleared → return to browse mode."""
        self._is_searching = False
        self._search_results = []
        self._search_capped = False

        if self._active_category_id and self._active_subcategory_id:
            self._on_subcategory_selected(
                self._active_category_id,
                self._active_subcategory_id
            )
        else:
            # No active selection? Show first subcategory
            self._category_tree._tree.setCurrentItem(
                self._category_tree._tree.topLevelItem(0).child(0)
            )

    def _focus_search(self):
        """Set focus to search bar."""
        self._search_bar.setFocus()
        self._search_bar.selectAll()

    # ═══════════════════════════════════════════════════════════════════════
    #  Copy Feedback
    # ═══════════════════════════════════════════════════════════════════════

    def _on_symbol_copied(self, symbol_data):
        """Show copy confirmation in status bar."""
        self._show_status(
            f'已复制: {symbol_data["char"]} ({symbol_data["name"]})',
            timeout=2500
        )

    # ═══════════════════════════════════════════════════════════════════════
    #  About Dialog
    # ═══════════════════════════════════════════════════════════════════════

    def _show_about(self):
        """Show About dialog."""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            '关于 Symbol Finder',
            '<h3>Symbol Finder</h3>'
            '<p>Windows 特殊符号查找工具</p>'
            f'<p>收录 {get_total_symbol_count()} 个特殊符号，</p>'
            '<p>涵盖 7 大类分类，支持中文搜索和一键复制。</p>'
            '<hr>'
            '<p>替代 Windows Win+. 面板中的 Ω 符号选项卡，</p>'
            '<p>解决无名称标注、无搜索功能的痛点。</p>'
            '<hr>'
            '<p>基于 PyQt5 构建 · 2026</p>'
        )
