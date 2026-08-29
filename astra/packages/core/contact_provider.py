from typing import List, Dict

class ContactProvider:
    """
    Simulates a local contact book for the resolution system.
    """
    def __init__(self):
        # A mocked database of contacts
        self.contacts = [
            {"name": "Kishan", "type": "person"},
            {"name": "Dhruv", "type": "person"},
            {"name": "Rishi", "type": "person"},
            {"name": "Susparin", "type": "person"},
            {"name": "Drogutta", "type": "person"}
        ]
        
    def get_contacts(self) -> List[Dict[str, str]]:
        return self.contacts
