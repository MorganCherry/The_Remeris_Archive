import sys
from pathlib import Path

def get_base_path() -> Path:
    """Returns the correct base folder whether running as .py script or bundled .exe"""
    try:
        return Path(sys._MEIPASS)  # PyInstaller onefile temp extraction folder
    except AttributeError:
        return Path(__file__).resolve().parent  # project root in dev mode

def resource_path(relative_path: str) -> Path:
    """Get absolute path to a bundled resource, e.g. resource_path('media/foo.png')"""
    return get_base_path() / relative_path