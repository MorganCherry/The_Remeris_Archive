"""Main window: chapter sidebar + rich text editor + toolbar + status bar."""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QLabel, QFileDialog, QInputDialog,
    QMessageBox, QToolBar, QLineEdit, QStackedWidget, QSizePolicy, QWidgetAction
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QActionGroup

from models import Book
from storage import save_book, load_book, is_valid_project
from ui.editor import ChapterEditor
from ui.format_bar import FormatBar
from ui.welcome_dialog import show_welcome_choice, run_new_book_wizard, show_setup_complete
from ui.themes import THEMES, apply_theme
from ui.paths import default_projects_folder
from ui.nag_wizard import IdleWatcher
from ui.tips_page import TipsPage
from ui.bunpack_page import BunPackPage
from ui.planning_page import PlanningPage
from ui.login_page import LoginPage
from ui.notes_dialog import NotesDialog
from ui import settings

PAGE_WRITING = 0
PAGE_TIPS = 1
PAGE_PLANNING = 2
PAGE_SHOP = 3
PAGE_LOGIN = 4


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The_Remeris_Archive")
        self.resize(1000, 700)

        self.book = Book()
        self.project_folder = None
        self.current_chapter = None
        self._loading = False
        self._word_baseline = 0

        self._build_menu()
        self._build_ui()

        saved_theme = settings.load_theme()
        apply_theme(self, saved_theme)
        self.format_bar.apply_theme_accent(saved_theme)
        self.login_page.apply_theme(saved_theme)
        for action in self._theme_actions:
            if action.text() == saved_theme:
                action.setChecked(True)

        self.idle_watcher = IdleWatcher(self, self.editor)

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self._autosave)
        self.autosave_timer.start(30_000)

        QTimer.singleShot(0, self._show_welcome_flow)


    # Menu bar 
    def _build_menu(self):
        # "View" is built here as a QMenu, but attached to a toolbar button
        # in _build_ui() instead of the native menu bar (keeps everything)
        # in one row instead of split across two.
        self.view_menu = self._build_view_menu()

    def _build_view_menu(self):
        from PySide6.QtWidgets import QMenu
        menu = QMenu("View", self)

        theme_menu = menu.addMenu("Theme")
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        self._theme_actions = []

        for theme_name in THEMES:
            action = QAction(theme_name, self, checkable=True)
            action.triggered.connect(lambda checked, name=theme_name: self._on_theme_selected(name))
            theme_group.addAction(action)
            theme_menu.addAction(action)
            self._theme_actions.append(action)

        return menu

    def _on_theme_selected(self, name: str):
        apply_theme(self, name)
        self.format_bar.apply_theme_accent(name)
        self.login_page.apply_theme(name)
        self.shop_page.apply_theme(name)
        settings.save_theme(name)


    # UI construction
    def _build_ui(self):
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)

        from PySide6.QtWidgets import QToolButton
        view_btn = QToolButton()
        view_btn.setText("View")
        view_btn.setMenu(self.view_menu)
        view_btn.setPopupMode(QToolButton.InstantPopup)
        toolbar.addWidget(view_btn)

        toolbar.addSeparator()

        new_action = QAction("New Book", self)
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)

        # Spacer pushes everything added after it to the far right of the toolbar
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        tips_action = QAction("Writing Tips", self)
        tips_action.triggered.connect(self.show_tips_page)
        toolbar.addAction(tips_action)

        planning_action = QAction("Planning", self)
        planning_action.triggered.connect(self.show_planning_page)
        toolbar.addAction(planning_action)

        shop_action = QAction("BunPack", self)
        shop_action.triggered.connect(self.show_shop_page)
        toolbar.addAction(shop_action)

        login_action = QAction("Login", self)
        login_action.triggered.connect(self.show_login_page)
        toolbar.addAction(login_action)

        central = QWidget()
        layout = QHBoxLayout(central)
        writing_page = QWidget()
        writing_layout = QHBoxLayout(writing_page)

        writing_layout.addWidget(self._build_sidebar())

        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)

        self.editor = ChapterEditor()
        self.editor.content_changed.connect(self._on_content_changed)

        self.format_bar = FormatBar(self.editor, on_notes_clicked=self._open_notes_dialog)
        editor_layout.addWidget(self.format_bar)
        editor_layout.addWidget(self.editor)

        self.status_label = QLabel("0 words")
        editor_layout.addWidget(self.status_label)

        writing_layout.addWidget(editor_container, stretch=1)

        self.tips_page = TipsPage(on_back=self.show_writing_page)
        self.planning_page = PlanningPage(
            get_book=lambda: self.book,
            on_change=self._on_planning_changed,
            on_back=self.show_writing_page,
        )
        self.shop_page = BunPackPage(on_back=self.show_writing_page)
        self.login_page = LoginPage(
            on_back=self.show_writing_page,
            get_login_count=settings.load_login_count,
            get_iq=settings.load_ink_quill,
            claim_login=settings.increment_login_count,
        )

        self.page_stack = QStackedWidget()
        self.page_stack.addWidget(writing_page)         # PAGE_WRITING
        self.page_stack.addWidget(self.tips_page)         # PAGE_TIPS
        self.page_stack.addWidget(self.planning_page)      # PAGE_PLANNING
        self.page_stack.addWidget(self.shop_page)           # PAGE_SHOP
        self.page_stack.addWidget(self.login_page)           # PAGE_LOGIN
        self.setCentralWidget(self.page_stack)

    def show_tips_page(self):
        self.tips_page.reload_content()
        self.page_stack.setCurrentIndex(PAGE_TIPS)

    def show_planning_page(self):
        self.planning_page.refresh()
        self.page_stack.setCurrentIndex(PAGE_PLANNING)

    def _on_planning_changed(self):
        """Called whenever a plot event or character is added/edited/deleted,
        so the change gets picked up by the normal autosave/save flow."""
        if self.project_folder:
            save_book(self.book, self.project_folder)

    def show_shop_page(self):
        self.page_stack.setCurrentIndex(PAGE_SHOP)

    def show_login_page(self):
        self.login_page.refresh()
        self.page_stack.setCurrentIndex(PAGE_LOGIN)

    def show_writing_page(self):
        self.page_stack.setCurrentIndex(PAGE_WRITING)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        self.book_title_edit = QLineEdit()
        self.book_title_edit.setPlaceholderText("Book title")
        self.book_title_edit.textChanged.connect(self._on_title_changed)
        sidebar_layout.addWidget(self.book_title_edit)

        self.chapter_list = QListWidget()
        self.chapter_list.setDragDropMode(QListWidget.InternalMove)
        self.chapter_list.model().rowsMoved.connect(self._on_chapters_reordered)
        self.chapter_list.currentItemChanged.connect(self._on_chapter_selected)
        sidebar_layout.addWidget(self.chapter_list)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ Chapter")
        add_btn.clicked.connect(self.add_chapter)
        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self.rename_chapter)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_chapter)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(rename_btn)
        btn_row.addWidget(delete_btn)
        sidebar_layout.addLayout(btn_row)

        sidebar.setFixedWidth(240)
        return sidebar


    # Guided start 
    def _show_welcome_flow(self):
        choice = show_welcome_choice(self)
        if choice == "new":
            self._guided_new_book()
        elif choice == "open":
            self.open_project()

    def _guided_new_book(self):
        book, project_folder = run_new_book_wizard(self)
        if book is None:
            return

        self.book = book
        self.project_folder = project_folder
        self.book_title_edit.setText(self.book.title)

        save_book(self.book, self.project_folder)
        settings.save_last_project_folder(self.project_folder)
        self._word_baseline = self.book.total_word_count()
        self._refresh_chapter_list()
        self.status_label.setText(f"Saved to {self.project_folder} · autosaving every 30s")

        show_setup_complete(self)


    # Project management
    def new_project(self):
        self._guided_new_book()

    def open_project(self):
        start_dir = str(default_projects_folder())
        folder = QFileDialog.getExistingDirectory(self, "Open Project Folder", start_dir)
        if not folder:
            return
        if not is_valid_project(folder):
            QMessageBox.warning(self, "Invalid Project", "That folder doesn't contain a project.json.")
            return
        self.book = load_book(folder)
        self.project_folder = folder
        settings.save_last_project_folder(folder)
        self._word_baseline = self.book.total_word_count()
        self.book_title_edit.setText(self.book.title)
        self._refresh_chapter_list()
        self.status_label.setText(f"Opened from {folder}")

    def save_project(self):
        self._sync_editor_to_current_chapter()
        if not self.project_folder:
            folder = QFileDialog.getExistingDirectory(
                self, "Choose Folder to Save Project", str(default_projects_folder())
            )
            if not folder:
                return
            self.project_folder = folder
            settings.save_last_project_folder(folder)
        self._accrue_ink_quill()
        save_book(self.book, self.project_folder)
        self.status_label.setText(f"Saved · {self.book.total_word_count()} words total")

    def _autosave(self):
        if self.project_folder:
            self._sync_editor_to_current_chapter()
            self._accrue_ink_quill()
            save_book(self.book, self.project_folder)
            self.status_label.setText(f"Autosaved · {self.book.total_word_count()} words total")

    def _accrue_ink_quill(self):
        current_total = self.book.total_word_count()
        net_new_words = current_total - self._word_baseline
        if net_new_words > 0:
            settings.add_ink_quill(net_new_words)
            self._word_baseline = current_total


    # Chapter management 
    def _refresh_chapter_list(self):
        self.chapter_list.clear()
        for chapter in self.book.chapters:
            item = QListWidgetItem(chapter.title)
            item.setData(Qt.UserRole, chapter.id)
            self.chapter_list.addItem(item)

        if not self.book.chapters:
            self.editor.clear()
            self.current_chapter = None
            return

        target_row = 0
        if self.book.last_chapter_id:
            for i in range(self.chapter_list.count()):
                if self.chapter_list.item(i).data(Qt.UserRole) == self.book.last_chapter_id:
                    target_row = i
                    break
        self.chapter_list.setCurrentRow(target_row)

    def add_chapter(self):
        chapter = self.book.add_chapter()
        self._refresh_chapter_list()
        for i in range(self.chapter_list.count()):
            if self.chapter_list.item(i).data(Qt.UserRole) == chapter.id:
                self.chapter_list.setCurrentRow(i)
                break

    def rename_chapter(self):
        if not self.current_chapter:
            return
        new_title, ok = QInputDialog.getText(self, "Rename Chapter", "Title:", text=self.current_chapter.title)
        if ok and new_title.strip():
            self.current_chapter.title = new_title.strip()
            self._refresh_chapter_list()

    def delete_chapter(self):
        if not self.current_chapter:
            return
        confirm = QMessageBox.question(
            self, "Delete Chapter", f"Delete '{self.current_chapter.title}'? This can't be undone."
        )
        if confirm == QMessageBox.Yes:
            self.book.remove_chapter(self.current_chapter.id)
            self._refresh_chapter_list()

    def _on_chapters_reordered(self, *args):
        new_order = []
        for i in range(self.chapter_list.count()):
            chapter_id = self.chapter_list.item(i).data(Qt.UserRole)
            chapter = self._find_chapter(chapter_id)
            if chapter:
                new_order.append(chapter)
        self.book.chapters = new_order

    def _on_chapter_selected(self, current, previous):
        if previous is not None:
            prev_id = previous.data(Qt.UserRole)
            prev_chapter = self._find_chapter(prev_id)
            if prev_chapter:
                prev_chapter.content = self.editor.toHtml()

        if current is None:
            self.current_chapter = None
            return

        chapter_id = current.data(Qt.UserRole)
        chapter = self._find_chapter(chapter_id)
        self.current_chapter = chapter
        self.book.last_chapter_id = chapter_id

        self._loading = True
        self.editor.setHtml(chapter.content if chapter else "")
        self.editor.randomize_placeholder()
        self.editor.set_font_family(self.format_bar.current_font_family())
        self.editor.set_font_size(self.format_bar.current_font_size())
        self.editor.set_text_color(self.format_bar.current_color())
        self._loading = False
        self._update_status()
        self.editor.setFocus()

    def _open_notes_dialog(self):
        if not self.current_chapter:
            QMessageBox.information(self, "No Chapter Selected", "Select or create a chapter first.")
            return

        dialog = NotesDialog(self.current_chapter.title, self.current_chapter.notes, self)
        dialog.exec()
        notes = dialog.get_notes()
        if notes is not None:  # None means Cancel was clicked
            self.current_chapter.notes = notes
            if self.project_folder:
                save_book(self.book, self.project_folder)

    def _find_chapter(self, chapter_id):
        return next((c for c in self.book.chapters if c.id == chapter_id), None)

    def _sync_editor_to_current_chapter(self):
        if self.current_chapter:
            self.current_chapter.content = self.editor.toHtml()


    # Misc handlers
    def _on_title_changed(self, text):
        self.book.title = text

    def _on_content_changed(self):
        if self._loading or not self.current_chapter:
            return
        self.current_chapter.content = self.editor.toHtml()
        self._update_status()

    def _update_status(self):
        chapter_words = self.editor.word_count()
        total_words = self.book.total_word_count()
        self.status_label.setText(f"{chapter_words} words in chapter · {total_words} words total")