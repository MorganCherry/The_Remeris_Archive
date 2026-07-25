"""The_Remeris_Archive - a creative writing space designed for storytellers. 
Write, organize, and develop your ideas in a focused environment built for imagination. 
Whether you create novels, short stories, journals, or entire worlds, grow your stories alongside a little mage bunny companion.."""
import sys
import ctypes
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow

from paths import resource_path

ICON_PATH = Path(__file__).resolve().parent / "media" / "BunMage_PNG_V1.7.png"

# Windows-only: tells the OS this app has its own identity, separate from
# Python itself, this is what fixes the taskbar icon showing the wrong image.
if sys.platform == "win32":
    app_id = "the_remeris_archive.writingapp.1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)


def main():
    app = QApplication(sys.argv)
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))

    window = MainWindow()
    if ICON_PATH.exists():
        window.setWindowIcon(QIcon(str(ICON_PATH)))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()