from typing import Dict, Any, Optional

class ReadingAssistant:
    """
    Maintains state for reading tasks (documents, web pages).
    Supports persisting the current reading position.
    """
    def __init__(self):
        self._current_document: str = ""
        self._paragraphs: list = []
        self._current_position: int = 0
        self._reading_mode: str = "FULL_READING"

    def load_document(self, document_name: str, content: str) -> None:
        """Loads a document and splits it into paragraphs."""
        self._current_document = document_name
        self._paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        self._current_position = 0

    def set_mode(self, mode: str) -> None:
        """Sets the reading mode (e.g., SUMMARY, HEADINGS_ONLY)."""
        valid_modes = ["FULL_READING", "SUMMARY", "HEADINGS_ONLY"]
        if mode in valid_modes:
            self._reading_mode = mode

    def get_next_paragraph(self) -> Optional[str]:
        """Returns the next paragraph and advances the reading position."""
        if self._current_position < len(self._paragraphs):
            paragraph = self._paragraphs[self._current_position]
            self._current_position += 1
            return paragraph
        return None

    def get_current_state(self) -> Dict[str, Any]:
        """Returns the saved reading position state."""
        return {
            "document": self._current_document,
            "position": self._current_position,
            "total_paragraphs": len(self._paragraphs),
            "mode": self._reading_mode
        }
