import os
import sys
import shutil
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from PySide6.QtCore import (
    Qt, QThread, Signal, QObject, QSettings, QSize,
)
from PySide6.QtGui import (
    QAction, QKeySequence, QFont,
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QFileDialog, QMessageBox,
    QStatusBar, QMenuBar, QMenu, QSizePolicy, QStyleFactory,
    QSplitter, QTreeWidget, QTreeWidgetItem, QHeaderView, QGroupBox,
    QToolBar, QAbstractItemView,
)

ORGANIZATION_NAME = "Danrex"
APPLICATION_NAME  = "Danrex Sorter"
APPLICATION_VERSION = "2.0.0"

ACCENT_COLOR    = "#0078D4"
FONT_FAMILY     = "Segoe UI"
MONOSPACE_FONT  = "Consolas"
BASE_FONT_SIZE  = 9

FILE_CATEGORIES: dict[str, list[str]] = {
    "Изображения": [
        ".jpg", ".jpeg", ".jpe", ".jfif", ".jif", ".jp2", ".j2k", ".jpx",
        ".jpm", ".mj2", ".png", ".apng", ".gif", ".bmp", ".dib", ".webp",
        ".svg", ".svgz", ".ico", ".tiff", ".tif", ".heic", ".heif", ".avif",
        ".raw", ".cr2", ".cr3", ".nef", ".arw", ".orf", ".rw2", ".dng",
        ".psd", ".psb", ".ai", ".eps", ".cdr", ".xcf", ".pcx", ".tga",
        ".icns", ".hdr", ".exr", ".ppm", ".pgm", ".pbm", ".pnm",
    ],
    "Документы": [
        ".pdf", ".doc", ".docx", ".docm", ".dot", ".dotx", ".odt", ".rtf",
        ".txt", ".text", ".md", ".markdown", ".csv", ".tsv", ".xls", ".xlsx",
        ".xlsm", ".xlt", ".xltx", ".ods", ".ppt", ".pptx", ".pptm", ".pot",
        ".potx", ".odp", ".odg", ".pages", ".numbers", ".key", ".tex",
        ".bib", ".log", ".ini", ".cfg", ".conf", ".yaml", ".yml", ".json",
        ".xml", ".html", ".htm", ".xhtml", ".epub", ".mobi", ".azw", ".fb2",
        ".djvu", ".chm", ".wps", ".wpd",
    ],
    "Видео": [
        ".mp4", ".m4v", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".f4v",
        ".webm", ".mpg", ".mpeg", ".mpe", ".m2v", ".m4p", ".m4b", ".3gp",
        ".3g2", ".ogv", ".ogg", ".rm", ".rmvb", ".asf", ".vob", ".ts",
        ".mts", ".m2ts", ".divx", ".xvid",
    ],
    "Аудио": [
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".oga", ".wma", ".m4a",
        ".opus", ".aiff", ".aif", ".ape", ".alac", ".ac3", ".dts", ".amr",
        ".mid", ".midi", ".mka", ".ra", ".au", ".pcm",
    ],
    "Архивы": [
        ".zip", ".zipx", ".rar", ".7z", ".tar", ".gz", ".gzip", ".bz2",
        ".bzip2", ".xz", ".lz", ".lzma", ".z", ".cab", ".iso", ".dmg",
        ".tgz", ".tbz2", ".txz", ".tar.gz", ".tar.bz2", ".tar.xz",
    ],
    "Программы": [
        ".exe", ".msi", ".apk", ".app", ".bat", ".cmd", ".sh", ".ps1",
        ".py", ".js", ".ts", ".java", ".class", ".jar", ".c", ".cpp",
        ".h", ".hpp", ".cs", ".rb", ".go", ".rs", ".swift", ".kt", ".php",
        ".pl", ".r", ".lua", ".sql", ".ipynb",
    ],
    "Шрифты": [
        ".ttf", ".otf", ".woff", ".woff2", ".eot", ".ttc", ".dfont",
        ".pfa", ".pfb",
    ],
    "Базы данных": [
        ".db", ".sqlite", ".sqlite3", ".mdb", ".accdb", ".dbf", ".frm",
        ".ibd", ".myd", ".myi",
    ],
}

DARK_THEME_STYLESHEET = f"""
QWidget {{
    font-family: "{FONT_FAMILY}";
    font-size: {BASE_FONT_SIZE}pt;
    color: #cccccc;
}}
QMainWindow, QDialog {{
    background-color: #1e1e1e;
}}
QMenuBar {{
    background-color: #2d2d2d;
    color: #cccccc;
    border-bottom: 1px solid #3e3e3e;
    padding: 0;
    spacing: 0;
}}
QMenuBar::item {{
    padding: 5px 10px;
    background: transparent;
}}
QMenuBar::item:selected {{
    background-color: #3e3e3e;
}}
QMenuBar::item:pressed {{
    background-color: #094771;
}}
QMenu {{
    background-color: #2d2d2d;
    color: #cccccc;
    border: 1px solid #3e3e3e;
    padding: 2px;
}}
QMenu::item {{
    padding: 5px 28px 5px 18px;
}}
QMenu::item:selected {{
    background-color: #094771;
    color: #ffffff;
}}
QMenu::separator {{
    height: 1px;
    background: #3e3e3e;
    margin: 3px 8px;
}}
QMenu::indicator {{
    width: 14px;
    height: 14px;
}}
QToolBar {{
    background-color: #252526;
    border-bottom: 1px solid #3e3e3e;
    spacing: 2px;
    padding: 2px 4px;
}}
QToolBar::separator {{
    width: 1px;
    background: #3e3e3e;
    margin: 3px 3px;
}}
QToolButton {{
    background-color: transparent;
    color: #cccccc;
    border: none;
    padding: 4px 10px;
    margin: 1px;
}}
QToolButton:hover {{
    background-color: #3e3e3e;
}}
QToolButton:pressed {{
    background-color: #094771;
}}
QGroupBox {{
    color: #cccccc;
    font-weight: bold;
    border: 1px solid #3e3e3e;
    background-color: #252526;
    margin-top: 14px;
    padding-top: 14px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    top: 0px;
    padding: 0 4px;
    color: #8fc9ff;
    background-color: #252526;
}}
QTreeWidget {{
    background-color: #252526;
    color: #cccccc;
    border: 1px solid #3e3e3e;
    alternate-background-color: #272727;
    outline: none;
    gridline-color: #3e3e3e;
}}
QTreeWidget::item {{
    padding: 3px 6px;
    border: none;
}}
QTreeWidget::item:selected {{
    background-color: #094771;
    color: #ffffff;
}}
QTreeWidget::item:hover:!selected {{
    background-color: #2a2d2e;
}}
QHeaderView {{
    background-color: #2d2d2d;
}}
QHeaderView::section {{
    background-color: #2d2d2d;
    color: #aaaaaa;
    padding: 4px 6px;
    border: none;
    border-right: 1px solid #3e3e3e;
    border-bottom: 1px solid #3e3e3e;
    font-weight: normal;
}}
QHeaderView::section:last {{
    border-right: none;
}}
QPushButton {{
    background-color: #3a3a3a;
    color: #cccccc;
    border: 1px solid #555555;
    padding: 4px 14px;
    min-height: 22px;
}}
QPushButton:hover {{
    background-color: #4a4a4a;
    border-color: #666666;
}}
QPushButton:pressed {{
    background-color: #2a2a2a;
}}
QPushButton:disabled {{
    background-color: #2d2d2d;
    color: #555555;
    border-color: #3a3a3a;
}}
QPushButton#AccentButton {{
    background-color: {ACCENT_COLOR};
    color: #ffffff;
    border: none;
    font-weight: bold;
    padding: 5px 18px;
    min-height: 26px;
}}
QPushButton#AccentButton:hover {{
    background-color: #1a8ad4;
}}
QPushButton#AccentButton:pressed {{
    background-color: #006cbe;
}}
QPushButton#AccentButton:disabled {{
    background-color: #2a4a6a;
    color: #666666;
}}
QProgressBar {{
    border: none;
    background-color: #3a3a3a;
    height: 4px;
    min-height: 4px;
    max-height: 4px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {ACCENT_COLOR};
}}
QScrollBar:vertical {{
    background: #252526;
    width: 12px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: #555555;
    min-height: 20px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background: #666666;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
    background: none;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
QStatusBar {{
    background-color: #2d2d2d;
    color: #cccccc;
    border-top: 1px solid #3e3e3e;
    padding: 0 8px;
    min-height: 20px;
    max-height: 20px;
}}
QStatusBar::item {{
    border: none;
}}
QStatusBar QLabel {{
    color: #cccccc;
    font-size: 8pt;
    padding: 0;
    background: transparent;
}}
QLabel {{
    color: #cccccc;
    background: transparent;
}}
QLabel#TitleLabel {{
    font-size: 14pt;
    font-weight: 300;
    color: #e0e0e0;
}}
QLabel#VersionLabel {{
    font-size: 8pt;
    color: #666666;
}}
QLabel#SubtitleLabel {{
    font-size: 8pt;
    color: #888888;
}}
QLabel#StatsLabel {{
    font-family: "{MONOSPACE_FONT}";
    font-size: 9pt;
    color: #888888;
}}
QLabel#PathLabel {{
    color: #888888;
    padding: 4px 8px;
    background-color: #252526;
    border: 1px solid #3e3e3e;
    font-size: 8pt;
}}
QSplitter::handle {{
    background-color: #3e3e3e;
}}
QSplitter::handle:horizontal {{
    width: 1px;
}}
"""

LIGHT_THEME_STYLESHEET = f"""
QWidget {{
    font-family: "{FONT_FAMILY}";
    font-size: {BASE_FONT_SIZE}pt;
    color: #1e1e1e;
}}
QMainWindow, QDialog {{
    background-color: #f0f0f0;
}}
QMenuBar {{
    background-color: #ffffff;
    color: #1e1e1e;
    border-bottom: 1px solid #d0d0d0;
    padding: 0;
    spacing: 0;
}}
QMenuBar::item {{
    padding: 5px 10px;
    background: transparent;
}}
QMenuBar::item:selected {{
    background-color: #e5e5e5;
}}
QMenuBar::item:pressed {{
    background-color: #cce4f7;
}}
QMenu {{
    background-color: #ffffff;
    color: #1e1e1e;
    border: 1px solid #c0c0c0;
    padding: 2px;
}}
QMenu::item {{
    padding: 5px 28px 5px 18px;
}}
QMenu::item:selected {{
    background-color: #cce4f7;
    color: #1e1e1e;
}}
QMenu::separator {{
    height: 1px;
    background: #e0e0e0;
    margin: 3px 8px;
}}
QToolBar {{
    background-color: #fafafa;
    border-bottom: 1px solid #d0d0d0;
    spacing: 2px;
    padding: 2px 4px;
}}
QToolBar::separator {{
    width: 1px;
    background: #d0d0d0;
    margin: 3px 3px;
}}
QToolButton {{
    background-color: transparent;
    color: #1e1e1e;
    border: none;
    padding: 4px 10px;
    margin: 1px;
}}
QToolButton:hover {{
    background-color: #e5e5e5;
}}
QToolButton:pressed {{
    background-color: #cce4f7;
}}
QGroupBox {{
    color: #1e1e1e;
    font-weight: bold;
    border: 1px solid #c8c8c8;
    background-color: #ffffff;
    margin-top: 14px;
    padding-top: 14px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    top: 0px;
    padding: 0 4px;
    color: {ACCENT_COLOR};
    background-color: #ffffff;
}}
QTreeWidget {{
    background-color: #ffffff;
    color: #1e1e1e;
    border: 1px solid #c8c8c8;
    alternate-background-color: #f7f7f7;
    outline: none;
    gridline-color: #e0e0e0;
}}
QTreeWidget::item {{
    padding: 3px 6px;
    border: none;
}}
QTreeWidget::item:selected {{
    background-color: #cce4f7;
    color: #1e1e1e;
}}
QTreeWidget::item:hover:!selected {{
    background-color: #f0f0f0;
}}
QHeaderView {{
    background-color: #f0f0f0;
}}
QHeaderView::section {{
    background-color: #f0f0f0;
    color: #555555;
    padding: 4px 6px;
    border: none;
    border-right: 1px solid #d0d0d0;
    border-bottom: 1px solid #d0d0d0;
    font-weight: normal;
}}
QHeaderView::section:last {{
    border-right: none;
}}
QPushButton {{
    background-color: #ffffff;
    color: #1e1e1e;
    border: 1px solid #adadad;
    padding: 4px 14px;
    min-height: 22px;
}}
QPushButton:hover {{
    background-color: #e9e9e9;
    border-color: #999999;
}}
QPushButton:pressed {{
    background-color: #d9d9d9;
}}
QPushButton:disabled {{
    background-color: #f5f5f5;
    color: #aaaaaa;
    border-color: #d0d0d0;
}}
QPushButton#AccentButton {{
    background-color: {ACCENT_COLOR};
    color: #ffffff;
    border: none;
    font-weight: bold;
    padding: 5px 18px;
    min-height: 26px;
}}
QPushButton#AccentButton:hover {{
    background-color: #1a8ad4;
}}
QPushButton#AccentButton:pressed {{
    background-color: #006cbe;
}}
QPushButton#AccentButton:disabled {{
    background-color: #a8cce8;
    color: #ffffff;
}}
QProgressBar {{
    border: none;
    background-color: #e0e0e0;
    height: 4px;
    min-height: 4px;
    max-height: 4px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {ACCENT_COLOR};
}}
QScrollBar:vertical {{
    background: #f0f0f0;
    width: 12px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: #c0c0c0;
    min-height: 20px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background: #a0a0a0;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
    background: none;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
QStatusBar {{
    background-color: #ffffff;
    color: #1e1e1e;
    border-top: 1px solid #d0d0d0;
    padding: 0 8px;
    min-height: 20px;
    max-height: 20px;
}}
QStatusBar::item {{
    border: none;
}}
QStatusBar QLabel {{
    color: #1e1e1e;
    font-size: 8pt;
    padding: 0;
    background: transparent;
}}
QLabel {{
    color: #1e1e1e;
    background: transparent;
}}
QLabel#TitleLabel {{
    font-size: 14pt;
    font-weight: 300;
    color: #1e1e1e;
}}
QLabel#VersionLabel {{
    font-size: 8pt;
    color: #aaaaaa;
}}
QLabel#SubtitleLabel {{
    font-size: 8pt;
    color: #666666;
}}
QLabel#StatsLabel {{
    font-family: "{MONOSPACE_FONT}";
    font-size: 9pt;
    color: #666666;
}}
QLabel#PathLabel {{
    color: #555555;
    padding: 4px 8px;
    background-color: #ffffff;
    border: 1px solid #c8c8c8;
    font-size: 8pt;
}}
QSplitter::handle {{
    background-color: #d0d0d0;
}}
QSplitter::handle:horizontal {{
    width: 1px;
}}
"""


@dataclass
class ScanResult:
    total_files: int
    category_counts: dict[str, int]


class FileSorterLogic(QObject):
    progress_updated = Signal(int, int, int)
    sorting_finished = Signal(int, int, str)
    error_occurred   = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._sorting_active = False

    @property
    def is_sorting(self) -> bool:
        return self._sorting_active

    @staticmethod
    def get_category(extension: str) -> str:
        ext_lower = extension.lower()
        for category, extensions in FILE_CATEGORIES.items():
            if ext_lower in extensions:
                return category
        return "Остальное"

    @staticmethod
    def get_unique_filename(folder_path: str, filename: str) -> str:
        name, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename
        while os.path.exists(os.path.join(folder_path, new_filename)):
            new_filename = f"{name}_{counter}{ext}"
            counter += 1
        return new_filename

    def scan_folder(self, folder_path: str) -> ScanResult:
        stats: dict[str, int] = {cat: 0 for cat in FILE_CATEGORIES}
        stats["Остальное"] = 0
        total = 0
        try:
            for entry in os.scandir(folder_path):
                if entry.is_file():
                    total += 1
                    _, ext = os.path.splitext(entry.name)
                    cat = self.get_category(ext)
                    stats[cat] = stats.get(cat, 0) + 1
        except OSError as e:
            raise RuntimeError(f"Не удалось просканировать папку: {e}") from e
        return ScanResult(total, stats)

    def sort_files(self, folder_path: str) -> None:
        self._sorting_active = True
        moved = errors = 0
        try:
            files = [
                f for f in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, f))
            ]
            total = len(files)
            if total == 0:
                self.sorting_finished.emit(0, 0, folder_path)
                return
            for i, filename in enumerate(files):
                if not self._sorting_active:
                    break
                src = os.path.join(folder_path, filename)
                _, ext = os.path.splitext(filename)
                cat = self.get_category(ext)
                dst_dir = os.path.join(folder_path, cat)
                os.makedirs(dst_dir, exist_ok=True)
                unique = self.get_unique_filename(dst_dir, filename)
                dst = os.path.join(dst_dir, unique)
                try:
                    shutil.move(src, dst)
                    moved += 1
                except OSError:
                    errors += 1
                pct = int((i + 1) / total * 100)
                self.progress_updated.emit(pct, i + 1, total)
            self.sorting_finished.emit(moved, errors, folder_path)
        except OSError as e:
            self.error_occurred.emit(str(e))
        finally:
            self._sorting_active = False

    def cancel_sorting(self) -> None:
        self._sorting_active = False


class SortWorker(QThread):
    progress_updated = Signal(int, int, int)
    sorting_finished = Signal(int, int, str)
    error_occurred   = Signal(str)

    def __init__(self, logic: FileSorterLogic, folder_path: str) -> None:
        super().__init__()
        self.logic = logic
        self.folder_path = folder_path
        self.logic.progress_updated.connect(self.progress_updated)
        self.logic.sorting_finished.connect(self.sorting_finished)
        self.logic.error_occurred.connect(self.error_occurred)

    def run(self) -> None:
        self.logic.sort_files(self.folder_path)


class ThemeController:
    LIGHT  = "light"
    DARK   = "dark"
    SYSTEM = "system"

    @staticmethod
    def _is_system_dark() -> bool:
        if sys.platform != "win32":
            return False
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except Exception:
            return False

    @staticmethod
    def apply_theme(app: QApplication, theme_name: str) -> None:
        if theme_name == ThemeController.DARK:
            app.setStyleSheet(DARK_THEME_STYLESHEET)
        elif theme_name == ThemeController.LIGHT:
            app.setStyleSheet(LIGHT_THEME_STYLESHEET)
        else:
            if ThemeController._is_system_dark():
                app.setStyleSheet(DARK_THEME_STYLESHEET)
            else:
                app.setStyleSheet(LIGHT_THEME_STYLESHEET)


class DanrexSorterWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
        self.logic    = FileSorterLogic()
        self.worker: Optional[SortWorker] = None
        self.selected_folder: str = ""
        self.theme: str = self.settings.value("theme", ThemeController.SYSTEM)

        self.setWindowTitle(APPLICATION_NAME)
        self.setMinimumSize(900, 600)

        self._build_actions()
        self._build_menubar()
        self._build_toolbar()
        self._build_central()
        self._build_statusbar()

        self._restore_geometry()
        self._apply_theme()
        self._sync_theme_actions()

    def _build_actions(self) -> None:
        self.open_folder_action = QAction("&Выбрать папку...", self)
        self.open_folder_action.setShortcut(QKeySequence("Ctrl+O"))
        self.open_folder_action.setStatusTip("Выбрать папку для сортировки (Ctrl+O)")
        self.open_folder_action.triggered.connect(self._do_select_folder)

        self.refresh_action = QAction("&Обновить", self)
        self.refresh_action.setShortcut(QKeySequence("F5"))
        self.refresh_action.setStatusTip("Обновить статистику (F5)")
        self.refresh_action.triggered.connect(self._do_refresh)
        self.refresh_action.setEnabled(False)

        self.exit_action = QAction("&Выход", self)
        self.exit_action.setShortcut(QKeySequence("Alt+F4"))
        self.exit_action.triggered.connect(self.close)

        self.sort_action = QAction("&Сортировать", self)
        self.sort_action.setShortcut(QKeySequence("Ctrl+Return"))
        self.sort_action.setStatusTip("Начать сортировку файлов (Ctrl+Enter)")
        self.sort_action.triggered.connect(self._do_sort)
        self.sort_action.setEnabled(False)

        self.light_theme_action = QAction("&Светлая",   self, checkable=True)
        self.dark_theme_action  = QAction("&Тёмная",    self, checkable=True)
        self.system_theme_action = QAction("&Системная", self, checkable=True)
        self.light_theme_action.triggered.connect(lambda: self._change_theme(ThemeController.LIGHT))
        self.dark_theme_action.triggered.connect(lambda: self._change_theme(ThemeController.DARK))
        self.system_theme_action.triggered.connect(lambda: self._change_theme(ThemeController.SYSTEM))

        self.about_action = QAction("&О программе...", self)
        self.about_action.triggered.connect(self._do_about)

    def _build_menubar(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&Файл")
        file_menu.addAction(self.open_folder_action)
        file_menu.addAction(self.refresh_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        view_menu = menu_bar.addMenu("&Вид")
        theme_menu = view_menu.addMenu("&Тема")
        theme_menu.addAction(self.light_theme_action)
        theme_menu.addAction(self.dark_theme_action)
        theme_menu.addAction(self.system_theme_action)

        tools_menu = menu_bar.addMenu("&Инструменты")
        tools_menu.addAction(self.sort_action)

        help_menu = menu_bar.addMenu("&Справка")
        help_menu.addAction(self.about_action)

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Основная панель")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)

        toolbar.addAction(self.open_folder_action)
        toolbar.addAction(self.refresh_action)
        toolbar.addSeparator()
        toolbar.addAction(self.sort_action)

    def _build_central(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 12, 16, 10)
        layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)

        title_label = QLabel(APPLICATION_NAME)
        title_label.setObjectName("TitleLabel")
        header_layout.addWidget(title_label)

        version_label = QLabel(f"v{APPLICATION_VERSION}")
        version_label.setObjectName("VersionLabel")
        version_label.setAlignment(Qt.AlignBottom)
        header_layout.addWidget(version_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        self.folder_path_label = QLabel("Папка не выбрана")
        self.folder_path_label.setObjectName("PathLabel")
        self.folder_path_label.setMinimumHeight(26)
        self.folder_path_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.folder_path_label)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)

        left_root = QWidget()
        left_root.setMinimumWidth(180)
        left_root.setMaximumWidth(260)
        left_layout = QVBoxLayout(left_root)
        left_layout.setContentsMargins(0, 0, 6, 0)
        left_layout.setSpacing(8)

        actions_group = QGroupBox("Действия")
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setContentsMargins(10, 18, 10, 10)
        actions_layout.setSpacing(6)

        self.open_folder_button = QPushButton("Выбрать папку")
        self.open_folder_button.setMinimumHeight(26)
        self.open_folder_button.clicked.connect(self._do_select_folder)
        actions_layout.addWidget(self.open_folder_button)

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.setEnabled(False)
        self.refresh_button.clicked.connect(self._do_refresh)
        actions_layout.addWidget(self.refresh_button)

        self.sort_button = QPushButton("Сортировать")
        self.sort_button.setObjectName("AccentButton")
        self.sort_button.setEnabled(False)
        self.sort_button.clicked.connect(self._do_sort)
        actions_layout.addWidget(self.sort_button)

        left_layout.addWidget(actions_group)

        progress_group = QGroupBox("Прогресс")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setContentsMargins(10, 18, 10, 10)
        progress_layout.setSpacing(6)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("Готов")
        self.progress_label.setObjectName("SubtitleLabel")
        self.progress_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_label)

        left_layout.addWidget(progress_group)
        left_layout.addStretch()

        splitter.addWidget(left_root)

        right_root = QWidget()
        right_layout = QVBoxLayout(right_root)
        right_layout.setContentsMargins(6, 0, 0, 0)
        right_layout.setSpacing(0)

        stats_group = QGroupBox("Статистика")
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setContentsMargins(8, 18, 8, 8)
        stats_layout.setSpacing(6)

        self.stats_tree = QTreeWidget()
        self.stats_tree.setHeaderLabels(["Категория", "Файлов", "Расширения"])
        self.stats_tree.setRootIsDecorated(False)
        self.stats_tree.setAlternatingRowColors(True)
        self.stats_tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.stats_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.stats_tree.setUniformRowHeights(True)
        self.stats_tree.setSortingEnabled(False)

        tree_header = self.stats_tree.header()
        tree_header.setStretchLastSection(True)
        tree_header.setSectionResizeMode(0, QHeaderView.Interactive)
        tree_header.setSectionResizeMode(1, QHeaderView.Fixed)
        tree_header.resizeSection(0, 140)
        tree_header.resizeSection(1, 64)

        stats_layout.addWidget(self.stats_tree)

        self.total_files_label = QLabel("Всего файлов: 0")
        self.total_files_label.setObjectName("StatsLabel")
        self.total_files_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        stats_layout.addWidget(self.total_files_label)

        right_layout.addWidget(stats_group)
        splitter.addWidget(right_root)

        splitter.setSizes([200, 600])
        layout.addWidget(splitter, stretch=1)

    def _build_statusbar(self) -> None:
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        self.status_main_label = QLabel("")
        status_bar.addWidget(self.status_main_label, 1)

        self.status_right_label = QLabel("")
        status_bar.addPermanentWidget(self.status_right_label)

    def _restore_geometry(self) -> None:
        saved_geometry = self.settings.value("geometry")
        was_maximized = self.settings.value("maximized", False, type=bool)
        if saved_geometry:
            self.restoreGeometry(saved_geometry)
        else:
            self.resize(1100, 720)
            self._center_on_screen()
        if was_maximized:
            self.showMaximized()

    def _center_on_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if screen:
            center = screen.availableGeometry().center()
            frame_geometry = self.frameGeometry()
            frame_geometry.moveCenter(center)
            self.move(frame_geometry.topLeft())

    def _apply_theme(self) -> None:
        app = QApplication.instance()
        if app:
            ThemeController.apply_theme(app, self.theme)

    def _sync_theme_actions(self) -> None:
        self.light_theme_action.setChecked(self.theme == ThemeController.LIGHT)
        self.dark_theme_action.setChecked(self.theme == ThemeController.DARK)
        self.system_theme_action.setChecked(self.theme == ThemeController.SYSTEM)

    def _change_theme(self, theme: str) -> None:
        self.theme = theme
        self.settings.setValue("theme", theme)
        self._apply_theme()
        self._sync_theme_actions()

    def _set_busy(self, busy: bool) -> None:
        self.open_folder_button.setEnabled(not busy)
        self.refresh_button.setEnabled(not busy and bool(self.selected_folder))
        self.sort_button.setEnabled(False)
        self.open_folder_action.setEnabled(not busy)
        self.refresh_action.setEnabled(not busy and bool(self.selected_folder))
        self.sort_action.setEnabled(False)
        if not busy:
            self._refresh_sort_button()

    def _refresh_sort_button(self) -> None:
        enabled = bool(self.selected_folder) and not self.logic.is_sorting
        self.sort_button.setEnabled(enabled)
        self.sort_action.setEnabled(enabled)

    def _update_status(self, text: str, right: str = "") -> None:
        self.status_main_label.setText(text)
        self.status_right_label.setText(right)

    def _do_select_folder(self) -> None:
        if self.logic.is_sorting:
            return
        folder = QFileDialog.getExistingDirectory(
            self, "Выберите папку для сортировки",
            self.selected_folder or str(Path.home()),
        )
        if folder:
            self.selected_folder = folder
            display_path = folder if len(folder) <= 80 else "..." + folder[-77:]
            self.folder_path_label.setText(display_path)
            self.folder_path_label.setToolTip(folder)
            self._scan_and_show()

    def _do_refresh(self) -> None:
        if self.selected_folder:
            self._scan_and_show()

    def _scan_and_show(self) -> None:
        self._update_status("Сканирование...")
        try:
            result = self.logic.scan_folder(self.selected_folder)
            self._populate_tree(result)
            has_files = result.total_files > 0
            self.refresh_button.setEnabled(True)
            self.refresh_action.setEnabled(True)
            self.sort_button.setEnabled(has_files)
            self.sort_action.setEnabled(has_files)
            if has_files:
                self._update_status(
                    "Готов к сортировке",
                    f"Найдено: {result.total_files} файл(ов)"
                )
            else:
                self._update_status("Файлов для сортировки не найдено")
        except RuntimeError as exc:
            QMessageBox.critical(self, "Ошибка сканирования", str(exc))
            self._update_status("Ошибка сканирования")

    def _populate_tree(self, result: ScanResult) -> None:
        self.stats_tree.clear()
        for category_name in FILE_CATEGORIES:
            count = result.category_counts.get(category_name, 0)
            if count == 0:
                continue
            extensions = FILE_CATEGORIES[category_name]
            sample = ", ".join(extensions[:6])
            if len(extensions) > 6:
                sample += "…"
            item = QTreeWidgetItem([category_name, str(count), sample])
            item.setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)
            self.stats_tree.addTopLevelItem(item)
        other_count = result.category_counts.get("Остальное", 0)
        if other_count:
            item = QTreeWidgetItem(["Остальное", str(other_count), "прочие расширения"])
            item.setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)
            self.stats_tree.addTopLevelItem(item)
        self.total_files_label.setText(f"Всего файлов: {result.total_files}")

    def _do_sort(self) -> None:
        if self.logic.is_sorting or not self.selected_folder:
            return
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Все файлы в папке\n\n  {self.selected_folder}\n\n"
            "будут распределены по подпапкам-категориям.\n\n"
            "Продолжить?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self._set_busy(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("0 / ?")
        self._update_status("Выполняется сортировка…")

        self.worker = SortWorker(self.logic, self.selected_folder)
        self.worker.progress_updated.connect(self._on_progress)
        self.worker.sorting_finished.connect(self._on_finished)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, pct: int, current: int, total: int) -> None:
        self.progress_bar.setValue(pct)
        self.progress_label.setText(f"{current} / {total}")
        self._update_status(
            "Выполняется сортировка…",
            f"{pct}%  ·  {current} из {total}"
        )

    def _on_finished(self, moved: int, errors: int, folder: str) -> None:
        self._set_busy(False)
        self.progress_bar.setValue(100)
        self.progress_label.setText("Завершено")
        self._update_status(
            "Сортировка завершена",
            f"Перемещено: {moved}"
            + (f"  ·  Ошибок: {errors}" if errors else "")
        )

        message = f"Сортировка завершена.\n\nПеремещено файлов: {moved}"
        if errors:
            message += f"\nОшибок при перемещении: {errors}"
        QMessageBox.information(self, "Готово", message)
        self._scan_and_show()

    def _on_error(self, message: str) -> None:
        self._set_busy(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("Ошибка")
        self._update_status("Ошибка при сортировке")
        QMessageBox.critical(self, "Ошибка", f"Произошла ошибка:\n\n{message}")

    def _do_about(self) -> None:
        QMessageBox.about(
            self,
            f"О программе {APPLICATION_NAME}",
            f"{APPLICATION_NAME}  {APPLICATION_VERSION}\n\n"
            "Автоматическая сортировка файлов по категориям\n"
            "на основе расширений.\n\n"
            "Поддерживаемые категории:\n"
            + ", ".join(FILE_CATEGORIES.keys())
            + ", Остальное.",
        )

    def closeEvent(self, event) -> None:
        if self.logic.is_sorting and self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Подтверждение выхода",
                "Сортировка выполняется. Прервать и выйти?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.logic.cancel_sorting()
                self.worker.quit()
                self.worker.wait()
            else:
                event.ignore()
                return

        self.settings.setValue("geometry",  self.saveGeometry())
        self.settings.setValue("maximized", self.isMaximized())
        event.accept()


def main() -> None:
    app = QApplication(sys.argv)
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setApplicationName(APPLICATION_NAME)

    if sys.platform == "win32":
        app.setStyle(QStyleFactory.create("windowsvista"))
    else:
        app.setStyle(QStyleFactory.create("Fusion"))

    font = QFont(FONT_FAMILY, BASE_FONT_SIZE)
    app.setFont(font)

    window = DanrexSorterWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
