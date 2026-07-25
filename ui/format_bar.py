"""Formatting bar: font picker, size (with big +/- buttons instead of the
tiny native spinner arrows), B/I/U (spaced apart), and a color swatch.
Remembers your last-used font, size, and color across app restarts."""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QFontComboBox, QSpinBox, QColorDialog,
    QAbstractSpinBox
)
from PySide6.QtGui import QColor, QFont

from ui import settings
from ui.themes import ACCENTS

MIN_FONT_SIZE = 6
MAX_FONT_SIZE = 96


class FormatBar(QWidget):
    """A row of formatting controls, wired directly to a ChapterEditor."""

    def __init__(self, editor, on_notes_clicked=None, parent=None):
        super().__init__(parent)
        self.editor = editor
        self._current_color = QColor(settings.load_text_color())
        self._current_theme = "Default"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 6)

        self.font_picker = QFontComboBox()
        self.font_picker.setFixedWidth(150)
        self.font_picker.setCurrentFont(QFont(settings.load_font_family()))
        self.font_picker.currentFontChanged.connect(self._on_font_changed)
        layout.addWidget(self.font_picker)

        layout.addSpacing(8)

        # Font size: big +/- buttons instead of the tiny native spin
        # arrows, which are notoriously hard to click accurately. (struggled 2 hours on this shit) Typing a
        # number directly into the box still works too.
        self.size_minus_btn = QPushButton("−")
        self.size_minus_btn.setFixedSize(28, 28)
        self.size_minus_btn.setToolTip("Decrease font size")
        self.size_minus_btn.clicked.connect(self._step_size_down)
        layout.addWidget(self.size_minus_btn)

        self.size_picker = QSpinBox()
        self.size_picker.setRange(MIN_FONT_SIZE, MAX_FONT_SIZE)
        self.size_picker.setValue(settings.load_font_size())
        self.size_picker.setFixedWidth(50)
        self.size_picker.setButtonSymbols(QAbstractSpinBox.NoButtons)  # hide tiny native arrows
        self.size_picker.valueChanged.connect(self._on_size_changed)
        layout.addWidget(self.size_picker)

        self.size_plus_btn = QPushButton("+")
        self.size_plus_btn.setFixedSize(28, 28)
        self.size_plus_btn.setToolTip("Increase font size")
        self.size_plus_btn.clicked.connect(self._step_size_up)
        layout.addWidget(self.size_plus_btn)

        layout.addSpacing(16)

        self.bold_btn = self._make_button("B", editor.toggle_bold, "Bold (Ctrl+B)")
        layout.addWidget(self.bold_btn)
        layout.addSpacing(8)

        self.italic_btn = self._make_button("I", editor.toggle_italic, "Italic (Ctrl+I)")
        layout.addWidget(self.italic_btn)
        layout.addSpacing(8)

        self.underline_btn = self._make_button("U", editor.toggle_underline, "Underline (Ctrl+U)")
        layout.addWidget(self.underline_btn)

        layout.addSpacing(16)

        self.color_btn = QPushButton("A")
        self.color_btn.setFixedWidth(32)
        self.color_btn.setToolTip("Text color for next typing (or selection)")
        self._update_color_swatch()
        self.color_btn.clicked.connect(self._pick_color)
        layout.addWidget(self.color_btn)

        layout.addSpacing(16)

        self.notes_btn = QPushButton("Notes")
        self.notes_btn.setToolTip("Add notes for the current chapter")
        if on_notes_clicked:
            self.notes_btn.clicked.connect(on_notes_clicked)
        layout.addWidget(self.notes_btn)

        layout.addStretch()

        editor.format_changed.connect(self._sync)

        self.editor.set_font_family(self.font_picker.currentFont().family())
        self.editor.set_font_size(self.size_picker.value())
        self.editor.set_text_color(self._current_color)

        self.apply_theme_accent(settings.load_theme())

    # Public helpers used by MainWindow

    def current_font_family(self) -> str:
        return self.font_picker.currentFont().family()

    def current_font_size(self) -> int:
        return self.size_picker.value()

    def current_color(self) -> QColor:
        return self._current_color

    def apply_theme_accent(self, theme_name: str):
        self._current_theme = theme_name
        accent = ACCENTS.get(theme_name, ACCENTS["Default"])
        checked_bg = accent["checked"]
        checked_fg = accent["checked_text"]

        style_map = {
            self.bold_btn: "font-weight: bold;",
            self.italic_btn: "font-style: italic;",
            self.underline_btn: "text-decoration: underline;",
        }
        for btn, base_style in style_map.items():
            btn.setStyleSheet(
                f"QPushButton {{ {base_style} }}"
                f"QPushButton:checked {{ background-color: {checked_bg}; "
                f"color: {checked_fg}; border: 2px solid {checked_bg}; }}"
            )

    # Internal 

    def _make_button(self, label, on_click, tooltip=""):
        btn = QPushButton(label)
        btn.setCheckable(True)
        btn.setFixedWidth(32)
        btn.setToolTip(tooltip)
        btn.clicked.connect(on_click)
        return btn

    def _step_size_up(self):
        self.size_picker.setValue(min(self.size_picker.value() + 1, MAX_FONT_SIZE))

    def _step_size_down(self):
        self.size_picker.setValue(max(self.size_picker.value() - 1, MIN_FONT_SIZE))

    def _on_font_changed(self, font):
        self.editor.set_font_family(font.family())
        settings.save_font_family(font.family())

    def _on_size_changed(self, size):
        self.editor.set_font_size(size)
        settings.save_font_size(size)

    def _pick_color(self):
        color = QColorDialog.getColor(self._current_color, self, "Pick Text Color")
        if color.isValid():
            self._current_color = color
            self.editor.set_text_color(color)
            self._update_color_swatch()
            settings.save_text_color(color.name())

    def _update_color_swatch(self):
        text_color = self._readable_text_color(self._current_color)
        self.color_btn.setStyleSheet(
            f"background-color: {self._current_color.name()}; "
            f"color: {text_color}; border: 2px solid #666; font-weight: bold;"
        )

    @staticmethod
    def _readable_text_color(bg: QColor) -> str:
        luminance = (0.299 * bg.red() + 0.587 * bg.green() + 0.114 * bg.blue())
        return "#000000" if luminance > 140 else "#ffffff"

    def _sync(self):
        self.bold_btn.setChecked(self.editor.is_bold())
        self.italic_btn.setChecked(self.editor.is_italic())
        self.underline_btn.setChecked(self.editor.is_underline())