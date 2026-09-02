from typing import List, Callable, Optional

class AACService:
    """
    Augmentative and Alternative Communication backend.
    Manages sentence construction from pictograms/phrases and provides predictions.
    """
    def __init__(self):
        self._current_sentence: List[str] = []
        self._vocabulary = ["I", "need", "want", "water", "help", "open", "calculator"]
        
    def select_word(self, word: str) -> None:
        """Adds a word/phrase to the current sentence buffer."""
        self._current_sentence.append(word)
        
    def get_predictions(self) -> List[str]:
        """Provides local fast predictions based on current context."""
        if not self._current_sentence:
            return ["I", "need", "help"]
            
        last_word = self._current_sentence[-1].lower()
        if last_word == "i":
            return ["need", "want", "am", "feel"]
        elif last_word == "open":
            return ["calculator", "youtube", "whatsapp"]
        return []

    def construct_message(self) -> str:
        """Assembles the current buffer into a full phrase string."""
        return " ".join(self._current_sentence)

    def speak_phrase(self, phrase: str) -> str:
        """Processes and records a spoken AAC phrase."""
        self.select_word(phrase)
        msg = self.construct_message()
        self.clear()
        return msg

    def clear(self) -> None:
        """Clears the buffer after execution."""
        self._current_sentence.clear()
