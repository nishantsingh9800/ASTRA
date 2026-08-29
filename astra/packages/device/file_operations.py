import os
import shutil
from typing import List, Dict, Any, Optional

class FileOperations:
    """
    Safe abstractions for filesystem interactions.
    Enforces permission checks for destructive operations.
    """
    def __init__(self, safe_mode: bool = True):
        self.safe_mode = safe_mode

    def read_file(self, filepath: str) -> Optional[str]:
        """Reads content from a file securely."""
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def create_file(self, filepath: str, content: str) -> bool:
        """Creates or overwrites a file."""
        if self.safe_mode and os.path.exists(filepath):
            raise PermissionError(f"Safe mode: Cannot overwrite existing file {filepath}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    def find_file(self, filename: str, directory: str = os.path.expanduser("~")) -> List[str]:
        """Searches for a file in a given directory."""
        results = []
        for root, dirs, files in os.walk(directory):
            if filename in files:
                results.append(os.path.join(root, filename))
        return results
