"""Color themes for The_Remeris_Archive, applied via the View > Theme menu."""

THEMES = {
    "Default": "",

    "Pink": """
        QMainWindow, QWidget { background-color: #fff0f5; color: #402030; }
        QMenuBar { background-color: #ffe4ec; color: #402030; }
        QMenuBar::item:selected { background-color: #ffb6c1; }
        QMenu { background-color: #fff8fa; color: #402030; }
        QMenu::item:selected { background-color: #ffb6c1; }
        QListWidget { background-color: #ffe4ec; border: 1px solid #ffc2d6; color: #402030; }
        QTextEdit { background-color: #fff8fa; border: 1px solid #ffc2d6; color: #402030; }
        QPushButton { background-color: #ffb6c1; border-radius: 6px; padding: 5px 10px; color: #402030; }
        QPushButton:hover { background-color: #ff9eb0; }
        QLineEdit { background-color: #fff8fa; border: 1px solid #ffc2d6; padding: 4px; color: #402030; }
        QSpinBox, QFontComboBox { background-color: #fff8fa; border: 1px solid #ffc2d6; padding: 2px; color: #402030; }
        QLabel { color: #402030; }
    """,

    "Blue": """
        QMainWindow, QWidget { background-color: #eaf4ff; color: #10283f; }
        QMenuBar { background-color: #dceeff; color: #10283f; }
        QMenuBar::item:selected { background-color: #a9d3ff; }
        QMenu { background-color: #f5faff; color: #10283f; }
        QMenu::item:selected { background-color: #a9d3ff; }
        QListWidget { background-color: #dceeff; border: 1px solid #a9d3ff; color: #10283f; }
        QTextEdit { background-color: #f5faff; border: 1px solid #a9d3ff; color: #10283f; }
        QPushButton { background-color: #a9d3ff; border-radius: 6px; padding: 5px 10px; color: #10283f; }
        QPushButton:hover { background-color: #8cc2ff; }
        QLineEdit { background-color: #f5faff; border: 1px solid #a9d3ff; padding: 4px; color: #10283f; }
        QSpinBox, QFontComboBox { background-color: #f5faff; border: 1px solid #a9d3ff; padding: 2px; color: #10283f; }
        QLabel { color: #10283f; }
    """,

    "Mint": """
        QMainWindow, QWidget { background-color: #eafff2; color: #103b26; }
        QMenuBar { background-color: #d7ffe8; color: #103b26; }
        QMenuBar::item:selected { background-color: #a3f0c2; }
        QMenu { background-color: #f4fff9; color: #103b26; }
        QMenu::item:selected { background-color: #a3f0c2; }
        QListWidget { background-color: #d7ffe8; border: 1px solid #a3f0c2; color: #103b26; }
        QTextEdit { background-color: #f4fff9; border: 1px solid #a3f0c2; color: #103b26; }
        QPushButton { background-color: #a3f0c2; border-radius: 6px; padding: 5px 10px; color: #103b26; }
        QPushButton:hover { background-color: #7fe6ac; }
        QLineEdit { background-color: #f4fff9; border: 1px solid #a3f0c2; padding: 4px; color: #103b26; }
        QSpinBox, QFontComboBox { background-color: #f4fff9; border: 1px solid #a3f0c2; padding: 2px; color: #103b26; }
        QLabel { color: #103b26; }
    """,

    "Lavender": """
        QMainWindow, QWidget { background-color: #f3ecff; color: #2e1a4d; }
        QMenuBar { background-color: #e5d8ff; color: #2e1a4d; }
        QMenuBar::item:selected { background-color: #c8adff; }
        QMenu { background-color: #faf6ff; color: #2e1a4d; }
        QMenu::item:selected { background-color: #c8adff; }
        QListWidget { background-color: #e5d8ff; border: 1px solid #c8adff; color: #2e1a4d; }
        QTextEdit { background-color: #faf6ff; border: 1px solid #c8adff; color: #2e1a4d; }
        QPushButton { background-color: #c8adff; border-radius: 6px; padding: 5px 10px; color: #2e1a4d; }
        QPushButton:hover { background-color: #b494ff; }
        QLineEdit { background-color: #faf6ff; border: 1px solid #c8adff; padding: 4px; color: #2e1a4d; }
        QSpinBox, QFontComboBox { background-color: #faf6ff; border: 1px solid #c8adff; padding: 2px; color: #2e1a4d; }
        QLabel { color: #2e1a4d; }
    """,

    "Dark": """
        QMainWindow, QWidget { background-color: #1e1e2e; color: #e0e0f0; }
        QMenuBar { background-color: #2a2a3d; color: #e0e0f0; }
        QMenuBar::item:selected { background-color: #44445c; }
        QMenu { background-color: #262637; color: #e0e0f0; }
        QMenu::item:selected { background-color: #44445c; }
        QListWidget { background-color: #2a2a3d; border: 1px solid #44445c; color: #e0e0f0; }
        QTextEdit { background-color: #262637; border: 1px solid #44445c; color: #e0e0f0; }
        QPushButton { background-color: #44445c; border-radius: 6px; padding: 5px 10px; color: #e0e0f0; }
        QPushButton:hover { background-color: #56567a; }
        QLineEdit { background-color: #262637; border: 1px solid #44445c; padding: 4px; color: #e0e0f0; }
        QSpinBox, QFontComboBox { background-color: #262637; border: 1px solid #44445c; padding: 2px; color: #e0e0f0; }
        QLabel { color: #e0e0f0; }
    """,
}

# Distinct "active/checked" accent colors per theme  (deliberately darker/more
# saturated than the theme's base button color, so a pressed Bold/Italic/
# Underline button is always clearly visible, regardless of theme.)
ACCENTS = {
    "Default":  {"checked": "#5b9bea", "checked_text": "#ffffff"},
    "Pink":     {"checked": "#ff6f91", "checked_text": "#ffffff"},
    "Blue":     {"checked": "#4488dd", "checked_text": "#ffffff"},
    "Mint":     {"checked": "#3fb87a", "checked_text": "#ffffff"},
    "Lavender": {"checked": "#8a5cdb", "checked_text": "#ffffff"},
    "Dark":     {"checked": "#7a7aa0", "checked_text": "#ffffff"},
}


def apply_theme(window, theme_name: str):
    """Apply a named theme's stylesheet to the given window."""
    window.setStyleSheet(THEMES.get(theme_name, ""))