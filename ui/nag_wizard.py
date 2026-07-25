"""The mad little wizard who gets pouty if you stop writing too long."""
import random
from pathlib import Path

from PySide6.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer

CAT_IMAGE_PATH = Path(__file__).resolve().parent.parent / "media" / "sad_cat.jpeg"

IDLE_TIMEOUT_MS = 5 * 60 * 1000  # 5 minutes

SCOLD_LINES = [
    "Oh, WONDERFUL. We're just... staring now. Cool. Cool cool cool.",
    "I have watched empires rise and fall faster than this paragraph.",
    "You know I can SEE the cursor not moving, right?",
    "Take your time. It's not like stories write themselves. Oh wait.",
    "Five minutes. FIVE. I've aged, scribe. I've physically aged.",
    "This is fine. I'm fine. The book is NOT fine, but sure, take a break.",
    "Ah yes, the ancient art of 'thinking about writing' instead of writing.",
    "I'm not mad. I'm just disappointed. Mostly mad though.",
]


class NagDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("...")

        layout = QHBoxLayout(self)

        image_label = QLabel()
        if CAT_IMAGE_PATH.exists():
            pixmap = QPixmap(str(CAT_IMAGE_PATH)).scaledToWidth(150, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
        else:
            image_label.setText("😿")
            image_label.setStyleSheet("font-size: 56px;")
        layout.addWidget(image_label)

        right = QVBoxLayout()
        message = QLabel(random.choice(SCOLD_LINES))
        message.setWordWrap(True)
        message.setFixedWidth(240)
        message.setStyleSheet("font-size: 14px; font-style: italic; padding: 6px 0 14px 0;")
        right.addWidget(message)

        ok_btn = QPushButton("...fine, I'll write.")
        ok_btn.clicked.connect(self.accept)
        right.addWidget(ok_btn)
        right.addStretch()

        layout.addLayout(right)

        if parent is not None:
            self._center_over_parent(parent)

    def _center_over_parent(self, parent):
        self.adjustSize()
        parent_center = parent.frameGeometry().center()
        geo = self.frameGeometry()
        geo.moveCenter(parent_center)
        self.move(geo.topLeft())


class IdleWatcher:
    """Watches for inactivity in the editor and pops up the nag dialog."""

    def __init__(self, main_window, editor):
        self.main_window = main_window
        self.editor = editor

        self.timer = QTimer(main_window)
        self.timer.setInterval(IDLE_TIMEOUT_MS)
        self.timer.timeout.connect(self._on_idle)
        self.timer.start()

        editor.content_changed.connect(self.reset)

    def reset(self):
        self.timer.start()

    def _on_idle(self):
        NagDialog(self.main_window).exec()
        self.reset()