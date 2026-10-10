# -*- coding: utf-8 -*-
"""
Symbol Finder — Windows 特殊符号查找工具

Entry point: launches the PyQt5 desktop application.

Usage:
    python main.py

The application is a desktop tool that catalogs special symbols from the
Windows Win+. (Omega tab) panel, organized hierarchically and searchable
by Chinese name. Each symbol can be copied to clipboard with one click.
"""
import sys
import os

# Ensure the app can find its modules when run from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from main_window import MainWindow
from theme_manager import load_theme, apply_theme


def main():
    """Application entry point."""
    # High-DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName('SymbolFinder')
    app.setOrganizationName('SymbolFinder')

    # Apply saved theme (or default dark)
    theme = load_theme()
    apply_theme(app, theme)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
