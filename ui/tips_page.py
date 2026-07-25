"""The 'Writing Tips' page renders a Markdown file of your own tips/links."""
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout, QLabel

from paths import resource_path

TIPS_FILE_PATH = Path(__file__).resolve().parent.parent / "content" / "tips.md"


class TipsPage(QWidget):
    """A simple Markdown-rendering page. Edit content/tips.md to change what shows here."""

    def __init__(self, on_back, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        header_row = QHBoxLayout()
        back_btn = QPushButton("← Back to Writing")
        back_btn.clicked.connect(on_back)
        header_row.addWidget(back_btn)
        header_row.addStretch()
        layout.addLayout(header_row)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)  # clicking a link opens it in your real browser
        layout.addWidget(self.browser)

        self.reload_content()

    def reload_content(self):
        """Re-reads the markdown file from disk. call this if you edit tips.md while the app is open."""
        if TIPS_FILE_PATH.exists():
            markdown_text = TIPS_FILE_PATH.read_text(encoding="utf-8")
        else:
            markdown_text = (
                "# No tips file found\n\n"
                f"Expected a file at `{TIPS_FILE_PATH}`. Create it and add your own "
                "writing tips, structured with Markdown headers."
            )
        self.browser.setMarkdown(markdown_text)