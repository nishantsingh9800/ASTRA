from typing import Optional, Dict

class ApplicationRegistry:
    """
    Maintains a cached registry of known applications and their executables/paths.
    Resolves natural language aliases (e.g. "calc", "visual studio") to executable commands.
    """
    def __init__(self):
        # Local deterministic map
        self.app_map: Dict[str, str] = {
            "calculator": "calc",
            "calc": "calc",
            "chrome": "chrome",
            "google chrome": "chrome",
            "whatsapp": "whatsapp://",
            "whats app": "whatsapp://",
            "whatsapp desktop": "whatsapp://",
            "notepad": "notepad",
            "vs code": "code",
            "visual studio code": "code",
            "code": "code",
            "word": "winword",
            "excel": "excel",
            "powerpoint": "powerpnt",
            "spotify": "spotify",
            "edge": "msedge"
        }
        self.pre_warm()

    def pre_warm(self):
        """
        In a production scenario, this would lightly scan common Start Menu shortcuts
        or cache them asynchronously. For now, we rely on the static deterministic map.
        """
        pass

    def resolve(self, app_name: str) -> str:
        """
        Resolves an application alias to its executable command.
        If it's not in the map, it returns the raw string assuming the OS PATH can handle it.
        """
        clean_name = app_name.lower().strip()
        return self.app_map.get(clean_name, clean_name)

    def get_known_aliases(self) -> list[str]:
        """Returns a list of all known application aliases for phonetic matching."""
        return list(self.app_map.keys())
