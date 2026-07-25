"""Handles saving and loading Book projects to/from disk as JSON."""
import json
from pathlib import Path
from models import Book

PROJECT_FILENAME = "project.json"


def save_book(book: Book, folder: str) -> None:
    """Save a book into the given project folder as project.json."""
    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)
    project_file = folder_path / PROJECT_FILENAME
    with open(project_file, "w", encoding="utf-8") as f:
        json.dump(book.to_dict(), f, indent=2, ensure_ascii=False)


def load_book(folder: str) -> Book:
    """Load a book from a project folder."""
    project_file = Path(folder) / PROJECT_FILENAME
    with open(project_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Book.from_dict(data)


def is_valid_project(folder: str) -> bool:
    return (Path(folder) / PROJECT_FILENAME).exists()
