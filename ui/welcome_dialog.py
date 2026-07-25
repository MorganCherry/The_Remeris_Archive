"""First-run welcome flow, featuring one (1) opinionated wizard bunny,
and the guided 'new book' wizard."""
import re
import random
from pathlib import Path

from PySide6.QtWidgets import (
    QMessageBox, QInputDialog, QFileDialog, QDialog, QLabel,
    QPushButton, QVBoxLayout, QHBoxLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QStandardPaths

from models import Book

from paths import resource_path

DEFAULT_PROJECTS_SUBFOLDER = "The_Remeris_Archive Projects"
BUNNY_IMAGE_PATH = Path(__file__).resolve().parent.parent / "media" / "BunMage_PNG_V1.7.png"

WELCOME_LINES = [
    "Ah, a new soul seeks the Quill. Sit. Let us begin the ritual.",
    "Mmm... I sense a story in you. A messy one. Perfect.",
    "Welcome, scribe. The blank page fears you already!",
    "I've waited centuries for someone with your... plot potential.",
    "Another writer. Wonderful. Try not to abandon this one halfway.",
]


def sanitize_folder_name(name: str) -> str:
    """Turn a book title into a safe folder name."""
    name = name.strip() or "Untitled Book"
    return re.sub(r'[<>:"/\\|?*]', "", name)


class _WelcomeDialog(QDialog):
    """Custom welcome popup: bunny portrait + a random wise-sassy greeting."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("The Remeris Archive")
        self.choice = "skip"

        layout = QHBoxLayout(self)

        image_label = QLabel()
        if BUNNY_IMAGE_PATH.exists():
            pixmap = QPixmap(str(BUNNY_IMAGE_PATH))
            pixmap = pixmap.scaledToWidth(180, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
        else:
            image_label.setText("🐰")
            image_label.setStyleSheet("font-size: 64px;")
        layout.addWidget(image_label)

        right = QVBoxLayout()

        greeting = QLabel(random.choice(WELCOME_LINES))
        greeting.setWordWrap(True)
        greeting.setStyleSheet("font-size: 14px; font-style: italic; padding: 6px 0 14px 0;")
        greeting.setFixedWidth(260)
        right.addWidget(greeting)

        new_btn = QPushButton("Start a New Book")
        new_btn.clicked.connect(lambda: self._pick("new"))
        open_btn = QPushButton("Open an Existing Book")
        open_btn.clicked.connect(lambda: self._pick("open"))
        skip_btn = QPushButton("Skip for now")
        skip_btn.clicked.connect(lambda: self._pick("skip"))

        right.addWidget(new_btn)
        right.addWidget(open_btn)
        right.addWidget(skip_btn)
        right.addStretch()

        layout.addLayout(right)

    def _pick(self, choice: str):
        self.choice = choice
        self.accept()


def show_welcome_choice(parent) -> str:
    """Show the bunny welcome popup. Returns 'new', 'open', or 'skip'."""
    dialog = _WelcomeDialog(parent)
    dialog.exec()
    return dialog.choice


def run_new_book_wizard(parent):
    """
    Walks the user through creating a new book: title, author, save location.
    Returns (book, project_folder) on success, or (None, None) if cancelled.
    """
    title, ok = QInputDialog.getText(parent, "New Book", "What's the title of your book?")
    if not ok or not title.strip():
        return None, None

    author, _ = QInputDialog.getText(parent, "New Book", "Author name (optional):")

    book = Book(title=title.strip(), author=author.strip())
    book.add_chapter("Chapter 1")

    project_folder = _choose_save_folder(parent, book)
    return book, project_folder


def _choose_save_folder(parent, book) -> str:
    documents_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
    default_root = Path(documents_path) / DEFAULT_PROJECTS_SUBFOLDER
    folder_name = sanitize_folder_name(book.title)
    suggested_folder = default_root / folder_name

    use_default = QMessageBox.question(
        parent,
        "Where should this be saved?",
        f"The_Remeris_Archive will save your book here:\n\n{suggested_folder}\n\n"
        "It will autosave automatically as you write. Use this location?",
        QMessageBox.Yes | QMessageBox.No,
    )

    if use_default == QMessageBox.Yes:
        return str(suggested_folder)

    chosen = QFileDialog.getExistingDirectory(parent, "Choose a Folder for This Book")
    return chosen if chosen else str(suggested_folder)


def show_setup_complete(parent):
    QMessageBox.information(
        parent,
        "You're all set!",
        "Your book has been created and saved. Just start writing."
        "The_Remeris_Archive will autosave every 30 seconds from now on.",
    )