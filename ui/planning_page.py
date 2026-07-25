"""The Planning page  - a Plottr-style outline board (chapters as columns,
event cards inside each) plus a Characters list, switchable via a small
sub-tab bar at the top."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame,
    QScrollArea, QInputDialog, QListWidget, QListWidgetItem, QStackedWidget,
    QMessageBox
)
from PySide6.QtCore import Qt

SUB_PLOT = 0
SUB_CHARACTERS = 1


class PlanningPage(QWidget):
    """get_book: callable returning the currently-open Book (live reference).
    on_change: callable to call after any edit, so the app knows to persist."""

    def __init__(self, get_book, on_change, on_back, parent=None):
        super().__init__(parent)
        self.get_book = get_book
        self.on_change = on_change

        layout = QVBoxLayout(self)

        header_row = QHBoxLayout()
        back_btn = QPushButton("← Back to Writing")
        back_btn.clicked.connect(on_back)
        header_row.addWidget(back_btn)

        header_row.addSpacing(20)

        self.plot_tab_btn = QPushButton("Plot")
        self.plot_tab_btn.setCheckable(True)
        self.plot_tab_btn.setChecked(True)
        self.plot_tab_btn.clicked.connect(lambda: self._switch_sub_page(SUB_PLOT))
        header_row.addWidget(self.plot_tab_btn)

        self.characters_tab_btn = QPushButton("Characters")
        self.characters_tab_btn.setCheckable(True)
        self.characters_tab_btn.clicked.connect(lambda: self._switch_sub_page(SUB_CHARACTERS))
        header_row.addWidget(self.characters_tab_btn)

        header_row.addStretch()
        layout.addLayout(header_row)

        self.sub_stack = QStackedWidget()
        layout.addWidget(self.sub_stack, stretch=1)

        self._build_plot_board()
        self._build_characters_page()


    # Sub-tab switching
    def _switch_sub_page(self, index: int):
        self.plot_tab_btn.setChecked(index == SUB_PLOT)
        self.characters_tab_btn.setChecked(index == SUB_CHARACTERS)
        self.sub_stack.setCurrentIndex(index)

    def refresh(self):
        """Call every time this page becomes visible (rebuilds from the
        current book, since chapters/events may have changed elsewhere.)"""
        self._rebuild_plot_board()
        self._rebuild_characters_list()


    # Plot board
    def _build_plot_board(self):
        board_page = QWidget()
        board_layout = QVBoxLayout(board_page)
        board_layout.setContentsMargins(0, 10, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.columns_container = QWidget()
        self.columns_layout = QHBoxLayout(self.columns_container)
        self.columns_layout.setAlignment(Qt.AlignLeft)
        scroll.setWidget(self.columns_container)

        board_layout.addWidget(scroll)
        self.sub_stack.addWidget(board_page)  # index SUB_PLOT

    def _rebuild_plot_board(self):
        # Clear existing columns
        while self.columns_layout.count():
            item = self.columns_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        book = self.get_book()
        for chapter in book.chapters:
            self.columns_layout.addWidget(self._build_chapter_column(chapter))

    def _build_chapter_column(self, chapter) -> QWidget:
        column = QFrame()
        column.setFixedWidth(220)
        column.setFrameShape(QFrame.StyledPanel)
        col_layout = QVBoxLayout(column)

        title_label = QLabel(chapter.title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_label.setAlignment(Qt.AlignCenter)
        col_layout.addWidget(title_label)

        book = self.get_book()
        for event in book.events_for_chapter(chapter.id):
            col_layout.addWidget(self._build_event_card(event))

        col_layout.addStretch()

        add_btn = QPushButton("+ Add Event")
        add_btn.clicked.connect(lambda: self._add_event(chapter.id))
        col_layout.addWidget(add_btn)

        return column

    def _build_event_card(self, event) -> QWidget:
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(4)

        title_row = QHBoxLayout()
        title_label = QLabel(event.title)
        title_label.setStyleSheet("font-weight: bold;")
        title_label.setWordWrap(True)
        title_row.addWidget(title_label, stretch=1)

        delete_btn = QPushButton("✕")
        delete_btn.setFixedSize(20, 20)
        delete_btn.setToolTip("Delete this event")
        delete_btn.clicked.connect(lambda: self._delete_event(event.id))
        title_row.addWidget(delete_btn)
        card_layout.addLayout(title_row)

        if event.description:
            desc_label = QLabel(event.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("font-size: 11px; color: gray;")
            card_layout.addWidget(desc_label)

        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self._edit_event(event.id))
        card_layout.addWidget(edit_btn)

        return card

    def _add_event(self, chapter_id: str):
        title, ok = QInputDialog.getText(self, "New Event", "Event title:")
        if not ok or not title.strip():
            return
        description, _ = QInputDialog.getText(self, "New Event", "Short description (optional):")

        book = self.get_book()
        book.add_plot_event(chapter_id, title.strip(), description.strip())
        self.on_change()
        self._rebuild_plot_board()

    def _edit_event(self, event_id: str):
        book = self.get_book()
        event = next((e for e in book.plot_events if e.id == event_id), None)
        if not event:
            return

        title, ok = QInputDialog.getText(self, "Edit Event", "Event title:", text=event.title)
        if not ok or not title.strip():
            return
        description, ok2 = QInputDialog.getText(
            self, "Edit Event", "Short description:", text=event.description
        )
        if not ok2:
            return

        event.title = title.strip()
        event.description = description.strip()
        self.on_change()
        self._rebuild_plot_board()

    def _delete_event(self, event_id: str):
        confirm = QMessageBox.question(self, "Delete Event", "Delete this event card?")
        if confirm == QMessageBox.Yes:
            book = self.get_book()
            book.remove_plot_event(event_id)
            self.on_change()
            self._rebuild_plot_board()


    # Characters
    def _build_characters_page(self):
        chars_page = QWidget()
        chars_layout = QHBoxLayout(chars_page)

        left_panel = QVBoxLayout()
        self.characters_list = QListWidget()
        self.characters_list.currentItemChanged.connect(self._on_character_selected)
        left_panel.addWidget(self.characters_list)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ Character")
        add_btn.clicked.connect(self._add_character)
        rename_btn = QPushButton("Edit")
        rename_btn.clicked.connect(self._edit_selected_character)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._delete_selected_character)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(rename_btn)
        btn_row.addWidget(delete_btn)
        left_panel.addLayout(btn_row)

        left_container = QWidget()
        left_container.setLayout(left_panel)
        left_container.setFixedWidth(240)
        chars_layout.addWidget(left_container)

        self.character_detail_label = QLabel("Select a character to see their details.")
        self.character_detail_label.setWordWrap(True)
        self.character_detail_label.setAlignment(Qt.AlignTop)
        self.character_detail_label.setStyleSheet("font-size: 14px; padding: 10px;")
        chars_layout.addWidget(self.character_detail_label, stretch=1)

        self.sub_stack.addWidget(chars_page)  # index SUB_CHARACTERS

    def _rebuild_characters_list(self):
        self.characters_list.clear()
        book = self.get_book()
        for character in book.characters:
            item = QListWidgetItem(character.name)
            item.setData(Qt.UserRole, character.id)
            self.characters_list.addItem(item)

    def _on_character_selected(self, current, previous):
        if current is None:
            self.character_detail_label.setText("Select a character to see their details.")
            return
        character_id = current.data(Qt.UserRole)
        book = self.get_book()
        character = next((c for c in book.characters if c.id == character_id), None)
        if character:
            text = f"{character.name}\n\n{character.description or '(no description yet)'}"
            self.character_detail_label.setText(text)

    def _add_character(self):
        name, ok = QInputDialog.getText(self, "New Character", "Character name:")
        if not ok or not name.strip():
            return
        description, _ = QInputDialog.getText(self, "New Character", "Short description (optional):")

        book = self.get_book()
        book.add_character(name.strip(), description.strip())
        self.on_change()
        self._rebuild_characters_list()

    def _edit_selected_character(self):
        item = self.characters_list.currentItem()
        if not item:
            return
        character_id = item.data(Qt.UserRole)
        book = self.get_book()
        character = next((c for c in book.characters if c.id == character_id), None)
        if not character:
            return

        name, ok = QInputDialog.getText(self, "Edit Character", "Name:", text=character.name)
        if not ok or not name.strip():
            return
        description, ok2 = QInputDialog.getText(
            self, "Edit Character", "Description:", text=character.description
        )
        if not ok2:
            return

        character.name = name.strip()
        character.description = description.strip()
        self.on_change()
        self._rebuild_characters_list()
        self._on_character_selected(item, None)

    def _delete_selected_character(self):
        item = self.characters_list.currentItem()
        if not item:
            return
        confirm = QMessageBox.question(self, "Delete Character", f"Delete '{item.text()}'?")
        if confirm == QMessageBox.Yes:
            character_id = item.data(Qt.UserRole)
            book = self.get_book()
            book.remove_character(character_id)
            self.on_change()
            self._rebuild_characters_list()