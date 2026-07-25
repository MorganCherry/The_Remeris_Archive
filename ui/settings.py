"""App-wide persisted settings (theme, font, size, color, last project folder,
login tracking, lifetime Ink Quill). Uses QSettings (stored in the Windows)
Registry / macOS plist / Linux config automatically, no extra file needed."""
import json
from datetime import date, timedelta
from PySide6.QtCore import QSettings

ORG_NAME = "CherryBunn"
APP_NAME = "The_Remeris_Archive"

WEEKLY_MILESTONE_DAYS = 3   # log in on this many distinct days this week...
WEEKLY_BONUS_IQ = 30        # ...to unlock this flat one-time bonus


def _settings() -> QSettings:
    return QSettings(ORG_NAME, APP_NAME)


def save_theme(name: str):
    s = _settings()
    s.setValue("theme", name)
    s.sync()


def load_theme(default: str = "Default") -> str:
    return _settings().value("theme", default)


def save_font_family(name: str):
    s = _settings()
    s.setValue("font_family", name)
    s.sync()


def load_font_family(default: str = "Georgia") -> str:
    return _settings().value("font_family", default)


def save_font_size(size: int):
    s = _settings()
    s.setValue("font_size", size)
    s.sync()


def load_font_size(default: int = 13) -> int:
    return int(_settings().value("font_size", default))


def save_text_color(hex_color: str):
    s = _settings()
    s.setValue("text_color", hex_color)
    s.sync()


def load_text_color(default: str = "#000000") -> str:
    return _settings().value("text_color", default)


def save_last_project_folder(folder: str):
    s = _settings()
    s.setValue("last_project_folder", folder)
    s.sync()


def load_last_project_folder(default=None):
    return _settings().value("last_project_folder", default)


def has_claimed_today() -> bool:
    last_claim = _settings().value("last_claim_date", "")
    return last_claim == date.today().isoformat()


def claim_login_for_today():
    """Call when the Login button is claimed. Only does anything the FIRST
    time this is called on a given real day (closing and reopening the app
    does NOT let you claim again until tomorrow.) Returns (claimed, new_count):
    claimed is False if today was already claimed (nothing changes)."""
    if has_claimed_today():
        return False, load_login_count()

    s = _settings()
    count = int(s.value("login_count", 0)) + 1
    s.setValue("login_count", count)
    s.setValue("last_claim_date", date.today().isoformat())
    s.sync()

    record_login_today()  # also mark today's weekday in the weekly tracker
    return True, count


def increment_login_count() -> int:
    """Lifetime, all-time count  (separate from the weekly tracker below.)"""
    s = _settings()
    count = int(s.value("login_count", 0)) + 1
    s.setValue("login_count", count)
    s.sync()
    return count


def load_login_count() -> int:
    return int(_settings().value("login_count", 0))


def add_ink_quill(amount: int) -> int:
    if amount <= 0:
        return load_ink_quill()
    s = _settings()
    total = int(s.value("lifetime_iq", 0)) + amount
    s.setValue("lifetime_iq", total)
    s.sync()
    return total


def load_ink_quill() -> int:
    return int(_settings().value("lifetime_iq", 0))


# ---------- Weekly login tracker ----------
# Stored as: {"week_start": "2026-06-29", "days": [0, 2, 4], "bonus_claimed": false}
# week_start is always the Monday of that week (ISO format).
# days are weekday indices, Monday=0 .. Sunday=6.

def _current_monday() -> str:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return monday.isoformat()


def _load_week_state() -> dict:
    s = _settings()
    raw = s.value("week_state", "")
    state = json.loads(raw) if raw else {}

    this_monday = _current_monday()
    if state.get("week_start") != this_monday:
        state = {"week_start": this_monday, "days": [], "bonus_claimed": False}
        s.setValue("week_state", json.dumps(state))
        s.sync()

    return state


def get_week_login_days() -> list:
    """Which weekdays (0=Mon..6=Sun) you've logged in on, this week only."""
    return _load_week_state().get("days", [])


def record_login_today() -> list:
    """Call when the Login button is claimed. Returns the updated day list."""
    state = _load_week_state()
    today_weekday = date.today().weekday()
    if today_weekday not in state["days"]:
        state["days"].append(today_weekday)
        s = _settings()
        s.setValue("week_state", json.dumps(state))
        s.sync()
    return state["days"]


def weekly_bonus_available() -> bool:
    state = _load_week_state()
    return len(state["days"]) >= WEEKLY_MILESTONE_DAYS and not state["bonus_claimed"]


def claim_weekly_bonus() -> int:
    """Grants the flat weekly IQ bonus once, if eligible. Returns new IQ total
    (unchanged if not eligible or already claimed)."""
    state = _load_week_state()
    if len(state["days"]) >= WEEKLY_MILESTONE_DAYS and not state["bonus_claimed"]:
        state["bonus_claimed"] = True
        s = _settings()
        s.setValue("week_state", json.dumps(state))
        s.sync()
        return add_ink_quill(WEEKLY_BONUS_IQ)
    return load_ink_quill()