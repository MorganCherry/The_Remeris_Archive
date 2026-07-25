"""Shared path helpers for The_Remeris_Archive."""
from pathlib import Path
from PySide6.QtCore import QStandardPaths

DEFAULT_PROJECTS_SUBFOLDER = "The_Remeris_Archive Projects"


def default_projects_folder() -> Path:
    """The default parent folder for all The_Remeris_Archive books, e.g.
    Documents/The_Remeris_Archive Projects. Created on disk if it doesn't exist yet."""
    documents_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
    folder = Path(documents_path) / DEFAULT_PROJECTS_SUBFOLDER
    folder.mkdir(parents=True, exist_ok=True)
    return folder