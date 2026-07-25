"""Core data structures for a The_Remeris_Archive project."""
from dataclasses import dataclass, field
from typing import List, Optional
import re
import uuid

_TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class Chapter:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Untitled Chapter"
    content: str = ""  # stored as HTML (rich text: bold/italic/underline)
    notes: str = ""  # freeform author notes for this chapter, plain text

    def word_count(self) -> int:
        plain_text = _TAG_RE.sub(" ", self.content)
        return len(plain_text.split())

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "content": self.content, "notes": self.notes}

    @staticmethod
    def from_dict(data: dict) -> "Chapter":
        return Chapter(
            id=data["id"],
            title=data["title"],
            content=data["content"],
            notes=data.get("notes", ""),
        )


@dataclass
class PlotEvent:
    """A single planning-board card - an outline note, not the actual prose."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    chapter_id: Optional[str] = None  # which chapter column this belongs to
    title: str = "Untitled Event"
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "chapter_id": self.chapter_id,
            "title": self.title,
            "description": self.description,
        }

    @staticmethod
    def from_dict(data: dict) -> "PlotEvent":
        return PlotEvent(
            id=data["id"],
            chapter_id=data.get("chapter_id"),
            title=data.get("title", "Untitled Event"),
            description=data.get("description", ""),
        )


@dataclass
class Character:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unnamed Character"
    description: str = ""

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "description": self.description}

    @staticmethod
    def from_dict(data: dict) -> "Character":
        return Character(
            id=data["id"],
            name=data.get("name", "Unnamed Character"),
            description=data.get("description", ""),
        )


@dataclass
class Book:
    title: str = "Untitled Book"
    author: str = ""
    chapters: List[Chapter] = field(default_factory=list)
    last_chapter_id: Optional[str] = None
    plot_events: List[PlotEvent] = field(default_factory=list)
    characters: List[Character] = field(default_factory=list)

    def total_word_count(self) -> int:
        return sum(ch.word_count() for ch in self.chapters)

    def add_chapter(self, title: str = None) -> Chapter:
        chapter = Chapter(title=title or f"Chapter {len(self.chapters) + 1}")
        self.chapters.append(chapter)
        return chapter

    def remove_chapter(self, chapter_id: str) -> None:
        self.chapters = [c for c in self.chapters if c.id != chapter_id]

    def add_plot_event(self, chapter_id: Optional[str], title: str, description: str = "") -> PlotEvent:
        event = PlotEvent(chapter_id=chapter_id, title=title, description=description)
        self.plot_events.append(event)
        return event

    def remove_plot_event(self, event_id: str) -> None:
        self.plot_events = [e for e in self.plot_events if e.id != event_id]

    def events_for_chapter(self, chapter_id: str) -> List[PlotEvent]:
        return [e for e in self.plot_events if e.chapter_id == chapter_id]

    def add_character(self, name: str, description: str = "") -> Character:
        character = Character(name=name, description=description)
        self.characters.append(character)
        return character

    def remove_character(self, character_id: str) -> None:
        self.characters = [c for c in self.characters if c.id != character_id]

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "author": self.author,
            "chapters": [c.to_dict() for c in self.chapters],
            "last_chapter_id": self.last_chapter_id,
            "plot_events": [e.to_dict() for e in self.plot_events],
            "characters": [c.to_dict() for c in self.characters],
        }

    @staticmethod
    def from_dict(data: dict) -> "Book":
        book = Book(title=data.get("title", "Untitled Book"), author=data.get("author", ""))
        book.chapters = [Chapter.from_dict(c) for c in data.get("chapters", [])]
        book.last_chapter_id = data.get("last_chapter_id")
        book.plot_events = [PlotEvent.from_dict(e) for e in data.get("plot_events", [])]
        book.characters = [Character.from_dict(c) for c in data.get("characters", [])]
        return book