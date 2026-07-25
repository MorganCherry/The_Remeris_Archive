"""The Login page (a weekly login tracker plus your Ink Quill total.)"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt

from ui.themes import ACCENTS
from ui import settings

WEEKDAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

IQ_EXPLANATION = (
    "Ink Quill (IQ) is your bunny's lifetime XP.\n\n"
    "It's earned only from words you actually write (net of edits), so "
    "rewriting a paragraph doesn't cost or gain anything extra.\n\n"
    "IQ never decreases. It's what levels up your bunny companion over time."
)


class LoginPage(QWidget):
    def __init__(self, on_back, get_login_count, get_iq, claim_login, parent=None):
        super().__init__(parent)
        self.get_login_count = get_login_count
        self.get_iq = get_iq
        self.claim_login = claim_login

        layout = QVBoxLayout(self)

        header_row = QHBoxLayout()
        back_btn = QPushButton("← Back to Writing")
        back_btn.clicked.connect(on_back)
        header_row.addWidget(back_btn)
        header_row.addStretch()
        layout.addLayout(header_row)

        layout.addStretch()

        title_label = QLabel("Welcome back")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; border: none;")
        layout.addWidget(title_label)

        self.count_label = QLabel()
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setStyleSheet("font-size: 13px; border: none;")
        layout.addWidget(self.count_label)

        layout.addSpacing(16)

        # The login card (only the interactive/claimable part gets a border)
        self.card = QFrame()
        self.card.setFrameShape(QFrame.StyledPanel)
        self.card.setFixedWidth(360)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(12)

        # Weekly day checkmarks (Mon..Sun) 
        week_row = QHBoxLayout()
        week_row.setSpacing(6)
        self.day_labels = []
        for name in WEEKDAY_LABELS:
            day_widget = QLabel()
            day_widget.setAlignment(Qt.AlignCenter)
            day_widget.setFixedSize(40, 40)
            day_widget.setToolTip(name)
            self.day_labels.append(day_widget)
            week_row.addWidget(day_widget)
        card_layout.addLayout(week_row)

        weekday_names_row = QHBoxLayout()
        weekday_names_row.setSpacing(6)
        for name in WEEKDAY_LABELS:
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedWidth(40)
            lbl.setStyleSheet("font-size: 10px; color: gray;")
            weekday_names_row.addWidget(lbl)
        card_layout.addLayout(weekday_names_row)

        self.claim_btn = QPushButton("Claim Login")
        self.claim_btn.clicked.connect(self._on_claim_clicked)
        card_layout.addWidget(self.claim_btn, alignment=Qt.AlignCenter)

        self.weekly_bonus_btn = QPushButton()
        self.weekly_bonus_btn.clicked.connect(self._on_claim_weekly_bonus)
        card_layout.addWidget(self.weekly_bonus_btn, alignment=Qt.AlignCenter)

        layout.addWidget(self.card, alignment=Qt.AlignCenter)

        # Ink Quill display, below the card
        self.iq_label = QLabel()
        self.iq_label.setAlignment(Qt.AlignCenter)
        self.iq_label.setStyleSheet("font-size: 16px; font-weight: bold; padding-top: 20px;")
        self.iq_label.setToolTip(IQ_EXPLANATION)
        layout.addWidget(self.iq_label)

        hint_label = QLabel("(hover the Ink Quill number above to see how it works)")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("font-size: 11px; color: gray;")
        layout.addWidget(hint_label)

        layout.addStretch()

        self._accent = ACCENTS["Default"]["checked"]
        self.apply_theme("Default")
        self.refresh()

    def apply_theme(self, theme_name: str):
        """Recolor the card border/accents to match the active theme."""
        self._accent = ACCENTS.get(theme_name, ACCENTS["Default"])["checked"]
        self.card.setStyleSheet(
            f"QFrame {{ border: 2px solid {self._accent}; border-radius: 16px; }}"
        )
        self.claim_btn.setStyleSheet(
            f"QPushButton {{ background-color: {self._accent}; color: white; "
            f"border-radius: 10px; padding: 8px 20px; font-weight: bold; }}"
            f"QPushButton:disabled {{ background-color: #999999; }}"
        )
        self.weekly_bonus_btn.setStyleSheet(
            f"QPushButton {{ background-color: transparent; color: {self._accent}; "
            f"border: 2px solid {self._accent}; border-radius: 10px; padding: 6px 16px; "
            f"font-weight: bold; }}"
            f"QPushButton:disabled {{ color: #999999; border-color: #999999; }}"
        )
        self._render_week_days()

    def refresh(self):
        """Call whenever the page becomes visible, to show current numbers."""
        count = self.get_login_count()
        self.count_label.setText(f"You've opened The_Remeris_Archive {count} time(s)")
        self.iq_label.setText(f"Ink Quill: {self.get_iq()}")

        self.claim_btn.setEnabled(not settings.has_claimed_today())
        self.claim_btn.setText(
            "Claimed for today" if settings.has_claimed_today() else "Claim Login"
        )

        self._render_week_days()
        self._render_weekly_bonus_button()

    def _render_week_days(self):
        logged_days = set(settings.get_week_login_days())
        for i, day_widget in enumerate(self.day_labels):
            if i in logged_days:
                day_widget.setText("✓")
                day_widget.setStyleSheet(
                    f"border: 2px solid {self._accent}; border-radius: 20px; "
                    f"background-color: {self._accent}; color: white; font-weight: bold;"
                )
            else:
                day_widget.setText("")
                day_widget.setStyleSheet(
                    f"border: 2px solid {self._accent}; border-radius: 20px; "
                    f"background-color: transparent;"
                )

    def _render_weekly_bonus_button(self):
        days_logged = len(settings.get_week_login_days())
        if settings.weekly_bonus_available():
            self.weekly_bonus_btn.setText(
                f"Claim Weekly Bonus (+{settings.WEEKLY_BONUS_IQ} IQ)"
            )
            self.weekly_bonus_btn.setEnabled(True)
        elif days_logged >= settings.WEEKLY_MILESTONE_DAYS:
            self.weekly_bonus_btn.setText("Weekly bonus claimed")
            self.weekly_bonus_btn.setEnabled(False)
        else:
            remaining = settings.WEEKLY_MILESTONE_DAYS - days_logged
            self.weekly_bonus_btn.setText(
                f"Log in {remaining} more day(s) this week for a bonus"
            )
            self.weekly_bonus_btn.setEnabled(False)

    def _on_claim_clicked(self):
        claimed, _ = settings.claim_login_for_today()
        self.refresh()

    def _on_claim_weekly_bonus(self):
        settings.claim_weekly_bonus()
        self.refresh()