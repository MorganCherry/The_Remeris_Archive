"""BunPack page (backpack / inventory view for The_Remeris_Archive)."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QSizePolicy, QPushButton, QScrollArea,
)
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from PySide6.QtWidgets import QMessageBox

from ui.themes import THEMES
from ui import settings



# Configuration 
_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media")
# NOTE: adjust this if your mp3 files live somewhere else
_AUDIO_DIR = os.path.join(_ASSETS_DIR, "audio")

_SLOT_LABELS = ["Cherry.mp3", "late_night.mp3", "", "", "", ""]
_SLOTS_COLS  = 3

_ENV_DATA = [
    ("candle",          "The Librarian's Candle",               "Reading Nook",        50),
    ("crystal_drop",    "Crystal Drop Pendant",                 "Stage: Rain",      75),
    ("magic_wand",      "Magic Wand",                           "Archmage spells",         100),
    ("crescent_moon",   "Crescent Moon Pendant",                "The Moon's Mystery",    80),
    ("firefly_jar",     "Firefly Jar",                          "Biologist's notes",          60),
    ("cherry_blossom",  "Cherry Blossom",                       "Cute EVERYTHING!",        55),
    ("seashell",        "Seashell",                             "Ocean whispers",          45),
    ("leaf",            "Leaf",                                 "Evening walk",            40),
    ("coffee_cup",      "Coffee Cup",                           "Morning Brew",            30),
    ("star",            "Star",                                 "Stargazing notes",        90),
]
_ENV_COLS = 3

_ENV_EMOJI = {
    "candle":         "🕯️",
    "crystal_drop":   "💧",
    "magic_wand":     "🪄",
    "crescent_moon":  "🌙",
    "firefly_jar":    "🫙",
    "cherry_blossom": "🌸",
    "seashell":       "🐚",
    "leaf":           "🍁",
    "coffee_cup":     "☕",
    "star":           "⭐",
}

_SLOT_STYLES = {
    "Default":  {"bg": "#ffffff", "border": "#d0d0d0", "text": "#000000", "empty_bg": "#f5f5f5", "empty_border": "#c0c0c0"},
    "Pink":     {"bg": "#ffe4ec", "border": "#ffb6c1", "text": "#402030", "empty_bg": "#fff8fa", "empty_border": "#ffc2d6"},
    "Blue":     {"bg": "#dceeff", "border": "#a9d3ff", "text": "#10283f", "empty_bg": "#f5faff", "empty_border": "#c4dfff"},
    "Mint":     {"bg": "#d7ffe8", "border": "#a3f0c2", "text": "#103b26", "empty_bg": "#f4fff9", "empty_border": "#b8f0d0"},
    "Lavender": {"bg": "#e5d8ff", "border": "#c8adff", "text": "#2e1a4d", "empty_bg": "#faf6ff", "empty_border": "#d4c0ff"},
    "Dark":     {"bg": "#2a2a3d", "border": "#44445c", "text": "#e0e0f0", "empty_bg": "#262637", "empty_border": "#3a3a50"},
}

_BADGE_COLORS = {
    "Default":  {"bg": "#ffffff", "text": "#000000", "sub": "#555555"},
    "Pink":     {"bg": "#fff0f5", "text": "#402030", "sub": "#7a5060"},
    "Blue":     {"bg": "#eaf4ff", "text": "#10283f", "sub": "#406080"},
    "Mint":     {"bg": "#eafff2", "text": "#103b26", "sub": "#407050"},
    "Lavender": {"bg": "#f3ecff", "text": "#2e1a4d", "sub": "#6a5090"},
    "Dark":     {"bg": "#262637", "text": "#e0e0f0", "sub": "#a0a0c0"},
}

# Smaller fractions so the bag doesn't dominate
_BP_MAX_W_FRAC = 0.20
_BP_MAX_H_FRAC = 0.50



# Helpers 
def _load(name: str) -> QPixmap:
    return QPixmap(os.path.join(_ASSETS_DIR, name))


def _ceil_div(a, b):
    return -(-a // b)


def _get_theme_name():
    return settings.load_theme()


def _current_slot_style():
    return _SLOT_STYLES.get(_get_theme_name(), _SLOT_STYLES["Default"])


def _current_badge():
    return _BADGE_COLORS.get(_get_theme_name(), _BADGE_COLORS["Default"])



# ItemSlot 
class ItemSlot(QPushButton):
    def __init__(self, text="", style=None, parent=None):
        super().__init__(parent)
        self._text = text
        self._pixmap = None
        self._style = style or _current_slot_style()
        self._playing = False
        self._build()

    def _build(self):
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(70, 50)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)

        display = self._text if self._text else "+"
        self._lbl = QLabel(display)
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl.setWordWrap(True)
        self._lbl.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        lay.addWidget(self._lbl)

        self._apply_style()

    def _apply_style(self):
        s = self._style
        if self._text:
            self._lbl.setStyleSheet(f"color: {s['text']}; background:transparent;")
            border_color = s['text'] if self._playing else s['border']
            self.setStyleSheet(
                f"QPushButton {{ background-color: {s['bg']}; border: 2px solid {border_color}; "
                f"border-radius: 8px; }}"
                f"QPushButton:hover {{ border: 2px solid {s['text']}; background-color: {s['border']}; }}"
            )
        else:
            self._lbl.setStyleSheet("color: grey; background:transparent;")
            self.setStyleSheet(
                f"QPushButton {{ background-color: {s['empty_bg']}; border: 2px dashed {s['empty_border']}; "
                f"border-radius: 8px; }}"
                f"QPushButton:hover {{ border: 2px solid {s['empty_border']}; border-style: solid; }}"
            )

    def set_theme_style(self, style: dict):
        self._style = style
        self._apply_style()

    def set_item(self, text, pixmap=None):
        self._text = text
        self._pixmap = pixmap
        self._refresh()

    def is_previewable(self) -> bool:
        return bool(self._text) and self._text.lower().endswith(".mp3")

    def set_playing(self, playing: bool):
        """Toggle the ▶ / ⏸ indicator shown on mp3 slots."""
        self._playing = playing
        self._refresh()

    def _refresh(self):
        if self._pixmap and not self._pixmap.isNull():
            self._lbl.setPixmap(self._pixmap.scaled(
                self._lbl.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        elif self._text:
            prefix = "⏸ " if self._playing else ("▶ " if self.is_previewable() else "")
            self._lbl.setText(prefix + self._text)
        else:
            self._lbl.setText("+")
        self._apply_style()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._pixmap and not self._pixmap.isNull():
            self._lbl.setPixmap(self._pixmap.scaled(
                self._lbl.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))



# EnvIcon
class EnvIcon(QWidget):
    unlock_requested = Signal(str, str, int)  # key, name, cost

    def __init__(self, key, name, desc, cost, badge=None, parent=None):
        super().__init__(parent)
        self._key = key
        self._name = name
        self._cost = cost
        self._orig = None
        self._badge = badge or _current_badge()
        self._unlocked = False

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(90, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet(
            "QWidget { background:transparent; border-radius:8px; }"
            "QWidget:hover { background:rgba(200,216,255,50); }"
        )

        px = _load(f"env_{key}.png")
        if not px.isNull():
            self._orig = px

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 2, 4, 6)
        lay.setSpacing(1)

        self._icon_lbl = QLabel()
        self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._icon_lbl.setAutoFillBackground(False)
        lay.addWidget(self._icon_lbl, stretch=1)

        self._name_lbl = QLabel(name)
        self._name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_lbl.setWordWrap(True)
        self._name_lbl.setAutoFillBackground(False)
        lay.addWidget(self._name_lbl)

        self._desc = desc
        self._info_lbl = QLabel(f"{cost} WF  ·  {desc}")
        self._info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._info_lbl.setWordWrap(True)
        self._info_lbl.setAutoFillBackground(False)
        lay.addWidget(self._info_lbl)

        self._apply_badge_style()

    def _apply_badge_style(self):
        bg, text, sub = self._badge["bg"], self._badge["text"], self._badge["sub"]
        self._name_lbl.setStyleSheet(
            f"background-color:{bg}; color:{text}; "
            f"font-size:11px; font-weight:bold; border-radius:4px; padding:2px 4px;"
        )
        self._info_lbl.setStyleSheet(
            f"background-color:{bg}; color:{sub}; "
            f"font-size:9px; border-radius:4px; padding:1px 4px;"
        )

    def set_badge(self, badge: dict):
        self._badge = badge
        self._apply_badge_style()

    def set_unlocked(self, unlocked: bool):
        """Mark this environment as purchased/unlocked and update its look."""
        self._unlocked = unlocked
        if unlocked:
            self._info_lbl.setText("✓ Unlocked")
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self._info_lbl.setText(f"{self._cost} WF  ·  {self._desc}")
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_badge_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self._unlocked:
            self.unlock_requested.emit(self._key, self._name, self._cost)
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w, h = self._icon_lbl.width(), self._icon_lbl.height()
        if w < 5 or h < 5:
            return
        if self._orig:
            self._icon_lbl.setPixmap(self._orig.scaled(
                w, h, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        else:
            side = min(w, h)
            self._icon_lbl.setFont(QFont("Segoe UI Emoji", max(16, side // 2)))
            self._icon_lbl.setText(_ENV_EMOJI.get(self._key, "❓"))



# StarryPanel
class StarryPanel(QWidget):
    unlock_requested = Signal(str, str, int)  # key, name, cost

    def __init__(self, badge=None, parent=None):
        super().__init__(parent)
        self._bg = _load("BunPack_bg.png")
        self._bp = _load("BunPack.png")
        self._badge = badge or _current_badge()
        self._env_icons: list = []
        self._icons_by_key: dict = {}
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(200)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(0)

        # Main row: LEFT column (desc + bag) | RIGHT column (icons)
        row = QHBoxLayout()
        row.setSpacing(16)

        # LEFT: description on top, backpack pinned to bottom
        left_col = QVBoxLayout()
        left_col.setSpacing(0)
        left_col.setContentsMargins(0, 0, 0, 0)

        desc = QLabel(
            "✦  Environments  ✦\n\n"
            "Each one sets the mood for\n"
            "your writing with immersive\n"
            "ambient soundscapes.\n\n"
            "Also comes with an exciting new theme!"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color:#c8d8ff; background:transparent;")
        desc.setWordWrap(True)
        desc.setFixedWidth(200)
        left_col.addWidget(desc)

        # Pushes the backpack all the way to the bottom of the left column
        left_col.addStretch()

        self._bp_lbl = QLabel()
        self._bp_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self._bp_lbl.setStyleSheet("background:transparent;")
        self._bp_lbl.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        left_col.addWidget(self._bp_lbl)

        row.addLayout(left_col, stretch=0)

        # RIGHT: scrollable 3x3 icon grid (gets ALL the vertical space)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea { background:transparent; border:none; }"
            "QScrollBar:vertical {"
            "  background:transparent; width:10px; margin:4px 2px 4px 2px;"
            "}"
            "QScrollBar::handle:vertical {"
            "  background:rgba(200,216,255,60); border-radius:5px; min-height:30px;"
            "}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
            "  height:0px;"
            "}"
        )

        grid_container = QWidget()
        grid_container.setStyleSheet("background:transparent;")
        grid = QGridLayout(grid_container)
        grid.setSpacing(10)
        grid.setContentsMargins(4, 4, 4, 4)

        for i, (key, name, d, cost) in enumerate(_ENV_DATA):
            icon = EnvIcon(key, name, d, cost, self._badge)
            icon.unlock_requested.connect(self.unlock_requested.emit)
            grid.addWidget(icon, *divmod(i, _ENV_COLS))
            self._env_icons.append(icon)
            self._icons_by_key[key] = icon

        for c in range(_ENV_COLS):
            grid.setColumnStretch(c, 1)
        for r in range(_ceil_div(len(_ENV_DATA), _ENV_COLS)):
            grid.setRowStretch(r, 0)

        scroll.setWidget(grid_container)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        row.addWidget(scroll, stretch=1)

        root.addLayout(row)

    def set_badge(self, badge: dict):
        self._badge = badge
        for icon in self._env_icons:
            icon.set_badge(badge)

    def mark_unlocked(self, key: str):
        icon = self._icons_by_key.get(key)
        if icon:
            icon.set_unlocked(True)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        if not self._bg.isNull():
            p.drawPixmap(self.rect(), self._bg)
        else:
            p.fillRect(self.rect(), QColor("#0a0a2e"))
        p.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self._bp.isNull():
            mw = int(self.width()  * _BP_MAX_W_FRAC)
            mh = int(self.height() * _BP_MAX_H_FRAC)
            self._bp_lbl.setPixmap(self._bp.scaled(
                mw, mh, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))



# BunPackPage
class BunPackPage(QWidget):
    def __init__(self, on_back=None, parent=None):
        super().__init__(parent)
        self._on_back = on_back
        self._starry_panel: StarryPanel | None = None
        self._slots: list[ItemSlot] = []

        # audio preview setup
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)
        self._player.playbackStateChanged.connect(self._on_playback_state_changed)
        self._current_slot: ItemSlot | None = None

        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        top = QHBoxLayout()

        if self._on_back:
            back_btn = QPushButton("← Back")
            back_btn.setFixedWidth(80)
            back_btn.clicked.connect(self._handle_back)
            top.addWidget(back_btn)

        heading = QLabel("These will be music mp3 to spend WF on")
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        top.addWidget(heading, stretch=1)

        if self._on_back:
            spacer = QWidget()
            spacer.setFixedWidth(80)
            top.addWidget(spacer)

        root.addLayout(top)

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setContentsMargins(0, 0, 0, 0)

        slot_style = _current_slot_style()
        for i, txt in enumerate(_SLOT_LABELS):
            slot = ItemSlot(txt, style=slot_style)
            if slot.is_previewable():
                slot.clicked.connect(lambda checked=False, s=slot: self._toggle_preview(s))
            grid.addWidget(slot, *divmod(i, _SLOTS_COLS))
            self._slots.append(slot)

        for c in range(_SLOTS_COLS):
            grid.setColumnStretch(c, 1)
        for r in range(_ceil_div(len(_SLOT_LABELS), _SLOTS_COLS)):
            grid.setRowStretch(r, 1)
        root.addLayout(grid, stretch=3)

        self._starry_panel = StarryPanel()
        self._starry_panel.unlock_requested.connect(self._handle_unlock_request)
        root.addWidget(self._starry_panel, stretch=7)

    
    #  preview playback
    def _toggle_preview(self, slot: ItemSlot):
        """Play/pause the mp3 tied to this slot. Only one preview plays at a time."""
        mp3_name = slot._text  # e.g. "Cherry.mp3"

        # Clicking the slot that's already playing -> pause it
        if self._current_slot is slot and self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
            slot.set_playing(False)
            return

        # Clicking the slot that's paused -> resume it
        if self._current_slot is slot and self._player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self._player.play()
            slot.set_playing(True)
            return

        # Switching to a different track: stop whatever was playing/paused
        if self._current_slot is not None and self._current_slot is not slot:
            self._current_slot.set_playing(False)

        path = os.path.join(_AUDIO_DIR, mp3_name)
        if not os.path.exists(path):
            print(f"[BunPack] preview file not found: {path}")
            return

        self._player.setSource(QUrl.fromLocalFile(path))
        self._player.play()
        self._current_slot = slot
        slot.set_playing(True)

    def _on_playback_state_changed(self, state):
        # Reset the slot's play and pause indicator once playback naturally stops (end of track)
        if state == QMediaPlayer.PlaybackState.StoppedState and self._current_slot is not None:
            self._current_slot.set_playing(False)
            self._current_slot = None

    def _handle_unlock_request(self, key: str, name: str, cost: int):
        reply = QMessageBox.question(
            self,
            "Unlock Item",
            f"Do you really want to buy \"{name}\" with your Ink Quills?\n\nCost: {cost} Ink Quills",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            # TODO: hook this up to your actual Ink Quills balance / save system
            self._starry_panel.mark_unlocked(key)

    def _handle_back(self):
        # Stop any preview before leaving the page
        self._player.stop()
        if self._on_back:
            self._on_back()

    def apply_theme(self, theme_name: str):
        slot_style = _SLOT_STYLES.get(theme_name, _SLOT_STYLES["Default"])
        for slot in self._slots:
            slot.set_theme_style(slot_style)

        badge = _BADGE_COLORS.get(theme_name, _BADGE_COLORS["Default"])
        if self._starry_panel:
            self._starry_panel.set_badge(badge)