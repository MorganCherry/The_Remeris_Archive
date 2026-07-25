"""A simple popup for jotting freeform notes on the current chapter."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QPlainTextEdit
)


class NotesDialog(QDialog):
    def __init__(self, chapter_title: str, existing_notes: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Notes - {chapter_title}")
        self.resize(420, 320)
        self._accepted_text = None

        layout = QVBoxLayout(self)

        label = QLabel(f"Notes for \"{chapter_title}\"")
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(label)

        self.text_box = QPlainTextEdit()
        self.text_box.setPlainText(existing_notes)
        self.text_box.setPlaceholderText(
            "Reminders, research, things to fix later, character notes for this scene..."
        )
        layout.addWidget(self.text_box, stretch=1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save Notes")
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        if parent is not None:
            self._center_over_parent(parent)

    def _center_over_parent(self, parent):
        self.adjustSize()
        parent_center = parent.frameGeometry().center()
        geo = self.frameGeometry()
        geo.moveCenter(parent_center)
        self.move(geo.topLeft())

    def _on_save(self):
        self._accepted_text = self.text_box.toPlainText()
        self.accept()

    def get_notes(self):
        """Returns the saved text, or None if the dialog was cancelled."""
        return self._accepted_text