"""A simple reusable 'coming soon' page (used for Planning and Shop until
their real content gets built out.)"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt


class PlaceholderPage(QWidget):
    def __init__(self, title: str, subtitle: str, on_back, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        header_row = QHBoxLayout()
        back_btn = QPushButton("← Back to Writing")
        back_btn.clicked.connect(on_back)
        header_row.addWidget(back_btn)
        header_row.addStretch()
        layout.addLayout(header_row)

        layout.addStretch()

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet("font-size: 14px; padding: 8px 40px;")
        layout.addWidget(subtitle_label)

        layout.addStretch()