# -*- coding: utf-8 -*-
"""
Theme Manager — Dark/Light theme system using Qt Style Sheets (QSS).

Design tokens are adapted from the web-based capacity converter tool:
    --color-bg          →  page / sidebar background
    --color-surface     →  card background
    --color-surface2    →  card hover / tree item hover
    --color-border      →  card borders, dividers
    --color-text        →  primary text
    --color-text2       →  secondary text
    --color-text3       →  muted text
    --color-accent      →  active highlight, focus ring
    --color-accent-hv   →  hover brightening
    --color-success     →  copied feedback flash
    --color-error       →  error state
"""
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QPalette, QColor


# ═══════════════════════════════════════════════════════════════════════════
#  Color Tokens (Dark Theme — default)
# ═══════════════════════════════════════════════════════════════════════════

DARK = {
    'bg':          '#0f172a',  # slate-900
    'surface':     '#1e293b',  # slate-800
    'surface2':    '#334155',  # slate-700
    'border':      '#475569',  # slate-600
    'text':        '#f1f5f9',  # slate-100
    'text2':       '#94a3b8',  # slate-400
    'text3':       '#64748b',  # slate-500
    'accent':      '#6366f1',  # indigo-500
    'accent_hv':   '#818cf8',  # indigo-400
    'success':     '#34d399',  # emerald-400
    'error':       '#f87171',  # red-400
    'accent_bg':   'rgba(99, 102, 241, 0.12)',
    'success_bg':  'rgba(52, 211, 153, 0.15)',
    'scrollbar_bg': '#1e293b',
    'scrollbar_hv': '#334155',
}


# ═══════════════════════════════════════════════════════════════════════════
#  Color Tokens (Light Theme)
# ═══════════════════════════════════════════════════════════════════════════

LIGHT = {
    'bg':          '#f8fafc',  # slate-50
    'surface':     '#ffffff',  # white
    'surface2':    '#f1f5f9',  # slate-100
    'border':      '#cbd5e1',  # slate-300
    'text':        '#0f172a',  # slate-900
    'text2':       '#475569',  # slate-600
    'text3':       '#94a3b8',  # slate-400
    'accent':      '#6366f1',  # indigo-500
    'accent_hv':   '#818cf8',  # indigo-400
    'success':     '#059669',  # emerald-600
    'error':       '#dc2626',  # red-600
    'accent_bg':   'rgba(99, 102, 241, 0.08)',
    'success_bg':  'rgba(5, 150, 105, 0.12)',
    'scrollbar_bg': '#f1f5f9',
    'scrollbar_hv': '#e2e8f0',
}


# ═══════════════════════════════════════════════════════════════════════════
#  Base QSS (structure-independent styles applied regardless of theme)
# ═══════════════════════════════════════════════════════════════════════════

BASE_QSS = """
/* ── Global ── */
QMainWindow {
    background-color: $bg$;
}
QWidget {
    font-family: "Microsoft YaHei", "Segoe UI", "PingFang SC", sans-serif;
    font-size: 13px;
}

/* ── Menubar ── */
QMenuBar {
    background-color: $surface$;
    color: $text$;
    border-bottom: 1px solid $border$;
    padding: 2px 0;
}
QMenuBar::item {
    padding: 4px 12px;
    background: transparent;
}
QMenuBar::item:selected {
    background-color: $accent_bg$;
    border-radius: 4px;
}
QMenu {
    background-color: $surface$;
    color: $text$;
    border: 1px solid $border$;
    padding: 4px;
}
QMenu::item {
    padding: 6px 28px 6px 16px;
}
QMenu::item:selected {
    background-color: $accent_bg$;
}
QMenu::separator {
    height: 1px;
    background: $border$;
    margin: 4px 8px;
}

/* ── Status Bar ── */
QStatusBar {
    background-color: $surface$;
    color: $text2$;
    border-top: 1px solid $border$;
    font-size: 12px;
    padding: 2px 8px;
}

/* ── Splitter ── */
QSplitter::handle {
    background-color: $border$;
    width: 1px;
}
QSplitter::handle:hover {
    background-color: $accent$;
}

/* ── Scrollbar (Vertical) ── */
QScrollBar:vertical {
    background: $bg$;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: $border$;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: $accent$;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

/* ── Scrollbar (Horizontal) ── */
QScrollBar:horizontal {
    background: $bg$;
    height: 8px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: $border$;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: $accent$;
}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ── Search Bar ── */
.search-bar {
    background-color: $surface$;
    border: 1px solid $border$;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 14px;
    color: $text$;
}
.search-bar:focus {
    border-color: $accent$;
}

/* ── Breadcrumb ── */
.breadcrumb {
    color: $text2$;
    font-size: 13px;
    padding: 4px 0;
}

/* ── Theme Toggle Button ── */
.theme-btn {
    background: $surface2$;
    border: 1px solid $border$;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 16px;
    color: $text$;
}
.theme-btn:hover {
    background: $accent_bg$;
    border-color: $accent$;
}

/* ── Title Label ── */
.title-label {
    font-size: 20px;
    font-weight: bold;
    color: $text$;
}
.subtitle-label {
    font-size: 12px;
    color: $text3$;
}
"""


# ═══════════════════════════════════════════════════════════════════════════
#  Card QSS (theme-dependent, kept separate for clarity)
# ═══════════════════════════════════════════════════════════════════════════

CARD_QSS = """
.symbol-card {
    background-color: $surface$;
    border: 1px solid $border$;
    border-radius: 12px;
    padding: 10px 6px;
}
.symbol-card:hover {
    background-color: $surface2$;
    border-color: $accent$;
}
.symbol-card:focus {
    border: 2px solid $accent$;
}

.symbol-char {
    font-size: 26px;
    color: $text$;
    font-family: "Segoe UI Symbol", "Segoe UI", "Arial Unicode MS", "Microsoft YaHei", sans-serif;
}
.symbol-name {
    font-size: 10px;
    color: $text2$;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
}
"""


# ═══════════════════════════════════════════════════════════════════════════
#  Category Tree QSS
# ═══════════════════════════════════════════════════════════════════════════

TREE_QSS = """
QTreeWidget {
    background-color: $bg$;
    color: $text$;
    border: none;
    outline: none;
    font-size: 13px;
}
QTreeWidget::item {
    padding: 5px 8px;
    border-radius: 4px;
    min-height: 28px;
}
QTreeWidget::item:hover {
    background-color: $surface2$;
}
QTreeWidget::item:selected {
    background-color: $accent_bg$;
    color: $accent$;
    font-weight: bold;
}

/* Category (top-level) items */
QTreeWidget::branch {
    background-color: $bg$;
}
QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {
    border-image: none;
}
QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings {
    border-image: none;
}
"""


# ═══════════════════════════════════════════════════════════════════════════
#  Theme Application
# ═══════════════════════════════════════════════════════════════════════════

SETTINGS_KEY = 'symbol-finder/theme'


def _compile_qss(template, tokens):
    """Replace $token$ placeholders in template with values from tokens dict."""
    result = template
    for key, value in tokens.items():
        result = result.replace('$' + key + '$', value)
    return result


def get_theme_qss(theme_name):
    """Return the complete QSS stylesheet for the given theme."""
    tokens = DARK if theme_name == 'dark' else LIGHT
    qss = _compile_qss(BASE_QSS, tokens)
    qss += _compile_qss(CARD_QSS, tokens)
    qss += _compile_qss(TREE_QSS, tokens)
    return qss


def apply_theme(app, theme_name):
    """Apply dark or light theme to the entire application."""
    qss = get_theme_qss(theme_name)
    app.setStyleSheet(qss)

    # Also update the QPalette for non-QSS-styled elements
    tokens = DARK if theme_name == 'dark' else LIGHT

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(tokens['bg']))
    palette.setColor(QPalette.WindowText, QColor(tokens['text']))
    palette.setColor(QPalette.Base, QColor(tokens['surface']))
    palette.setColor(QPalette.AlternateBase, QColor(tokens['surface2']))
    palette.setColor(QPalette.Text, QColor(tokens['text']))
    palette.setColor(QPalette.Button, QColor(tokens['surface']))
    palette.setColor(QPalette.ButtonText, QColor(tokens['text']))
    palette.setColor(QPalette.Highlight, QColor(tokens['accent']))
    palette.setColor(QPalette.HighlightedText, QColor('#ffffff'))
    app.setPalette(palette)


def load_theme():
    """Load saved theme from QSettings. Returns 'dark' or 'light'."""
    settings = QSettings('SymbolFinder', 'Theme')
    theme = settings.value(SETTINGS_KEY, 'dark')
    if theme not in ('dark', 'light'):
        theme = 'dark'
    return theme


def save_theme(theme_name):
    """Save theme preference to QSettings."""
    settings = QSettings('SymbolFinder', 'Theme')
    settings.setValue(SETTINGS_KEY, theme_name)


def toggle_theme(app):
    """Toggle between dark and light theme, return the new theme name."""
    current = load_theme()
    new_theme = 'light' if current == 'dark' else 'dark'
    apply_theme(app, new_theme)
    save_theme(new_theme)
    return new_theme
