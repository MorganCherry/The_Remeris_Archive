"""The chapter text editor widget (bold/italic/underline/color/size),
keyboard shortcuts, plus a grumpy-wise bunny who has opinions about
your empty page."""
import random
from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QFont, QShortcut, QKeySequence, QColor
from PySide6.QtCore import Signal, Qt

PLACEHOLDER_LINES = [
    "Start the lore. Build the characters. FEEL THE MAGIC.",
    "Go ahead... stare. The story won't write itself, y'know?",
    "The cursor blinks. It's judging you. Type something.",
    "Somewhere, a plot twist is waiting to be born. Get on with it.",
    "I have seen a thousand blank pages. This one's still winning.",
    "Ah, silence. My favorite sound... said no deadline ever.",
    "Write badly first. Fix it later. That's the whole secret.",
    "The page is patient... I, however, am not.",
]


class ChapterEditor(QTextEdit):
    """A rich text editor tuned for long-form writing."""

    content_changed = Signal()
    format_changed = Signal()  # fires when cursor formatting state changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.randomize_placeholder()
        self.setAcceptRichText(True)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setTabChangesFocus(False)
        self.setCursorWidth(2)  # thicker, more visible blinking caret

        font = QFont("Georgia")
        font.setPointSize(13)
        self.setFont(font)

        self.textChanged.connect(self.content_changed.emit)
        self.cursorPositionChanged.connect(self.format_changed.emit)
        self.currentCharFormatChanged.connect(lambda _: self.format_changed.emit())

        self._setup_shortcuts()

    def _setup_shortcuts(self):
        for keys, handler in (
            ("Ctrl+B", self.toggle_bold),
            ("Ctrl+I", self.toggle_italic),
            ("Ctrl+U", self.toggle_underline),
        ):
            shortcut = QShortcut(QKeySequence(keys), self)
            shortcut.setContext(Qt.WidgetWithChildrenShortcut)
            shortcut.activated.connect(handler)

    def randomize_placeholder(self):
        """Pick a new bunny one-liner for the empty-page placeholder text."""
        self.setPlaceholderText(random.choice(PLACEHOLDER_LINES))

    def word_count(self) -> int:
        text = self.toPlainText()
        return len(text.split())

    # Selection-aware formatting helpers
    #
    # The naive approach (just checking self.fontWeight()) only looks at ONE
    # point in the selection. If you select a bold word plus even a little
    # bit of non-bold text (very common double-click word selection often
    # grabs a trailing space), Qt reports the selection as "not bold", so
    # clicking Bold would make everything bold AGAIN instead of removing it.
    # These helpers scan the WHOLE selection instead, so toggling is only
    # considered "on" if every bit of the selection already has that format.

    def _selection_is_fully(self, predicate) -> bool:
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return predicate(cursor.charFormat())

        start, end = cursor.selectionStart(), cursor.selectionEnd()
        found_real_text = False
        block = self.document().findBlock(start)
        while block.isValid() and block.position() < end:
            it = block.begin()
            while not it.atEnd():
                frag = it.fragment()
                if frag.isValid():
                    frag_start = frag.position()
                    frag_end = frag_start + frag.length()
                    if frag_end > start and frag_start < end:
                        # Only look at the slice of this fragment that's
                        # actually inside the selection a fragment can span
                        # beyond the selection (e.g. " world" when only the
                        # leading space is selected), and checking the whole
                        # fragment's text would wrongly treat "world" as
                        # selected too.
                        overlap_start = max(frag_start, start)
                        overlap_end = min(frag_end, end)
                        substring = frag.text()[overlap_start - frag_start: overlap_end - frag_start]

                        # Whitespace-only overlap (e.g. a trailing space
                        # grabbed by word-selection) doesn't count either way.
                        # you can't visually tell if a space is bold, so it
                        # shouldn't force the whole selection into "mixed".
                        if substring.strip():
                            found_real_text = True
                            if not predicate(frag.charFormat()):
                                return False
                it += 1
            block = block.next()
        # If the selection was pure whitespace, fall back to the cursor's
        # own format rather than reporting a meaningless "True".
        return found_real_text or predicate(cursor.charFormat())

    def toggle_bold(self):
        make_bold = not self._selection_is_fully(lambda fmt: fmt.fontWeight() == QFont.Bold)
        self.setFontWeight(QFont.Bold if make_bold else QFont.Normal)

    def toggle_italic(self):
        make_italic = not self._selection_is_fully(lambda fmt: fmt.fontItalic())
        self.setFontItalic(make_italic)

    def toggle_underline(self):
        make_underline = not self._selection_is_fully(lambda fmt: fmt.fontUnderline())
        self.setFontUnderline(make_underline)

    def set_font_family(self, family: str):
        self.setFontFamily(family)

    def set_font_size(self, size: int):
        self.setFontPointSize(size)

    def set_text_color(self, color: QColor):
        self.setTextColor(color)

    def is_bold(self) -> bool:
        return self._selection_is_fully(lambda fmt: fmt.fontWeight() == QFont.Bold)

    def is_italic(self) -> bool:
        return self._selection_is_fully(lambda fmt: fmt.fontItalic())

    def is_underline(self) -> bool:
        return self._selection_is_fully(lambda fmt: fmt.fontUnderline())