from typing import Dict, Optional

class WebsiteRegistry:
    """
    Maintains a cached registry of known websites and their canonical URLs.
    Resolves natural language aliases (e.g., 'yt', 'gmail') to canonical websites.
    """
    def __init__(self):
        # Local deterministic map
        self.website_map: Dict[str, str] = {
            "youtube": "https://www.youtube.com/",
            "yt": "https://www.youtube.com/",
            "gmail": "https://mail.google.com/",
            "google mail": "https://mail.google.com/",
            "github": "https://github.com/",
            "git hub": "https://github.com/",
            "google drive": "https://drive.google.com/",
            "drive": "https://drive.google.com/",
            "wikipedia": "https://www.wikipedia.org/",
            "whatsapp web": "https://web.whatsapp.com/"
        }
        
    def resolve_alias(self, alias: str) -> str:
        """
        Resolves an alias to a recognized website canonical name.
        """
        clean_alias = alias.lower().strip()
        # Find the primary name if it maps to one of our URLs
        url = self.website_map.get(clean_alias)
        if url:
            # Reverse lookup the primary key (first key matching this url)
            for k, v in self.website_map.items():
                if v == url:
                    # In a real app we might have a strict canonical name, but for now we just return the first key or title case it
                    return k.title() if len(k) > 2 else k.upper()
        return alias.title()

    def resolve_url(self, website_name: str) -> str:
        """
        Resolves a website name to its canonical URL.
        """
        clean_name = website_name.lower().strip()
        return self.website_map.get(clean_name, f"https://www.{clean_name.replace(' ', '')}.com/")

    def is_known_website(self, name: str) -> bool:
        """
        Returns true if the name matches a known website alias.
        """
        return name.lower().strip() in self.website_map

    def resolve_website(self, alias: str) -> Dict[str, str]:
        """
        Resolves an alias to a structured target object.
        """
        url = self.resolve_url(alias)
        name = self.resolve_alias(alias)
        
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '') if parsed.netloc else ""
        
        return {
            "type": "WEBSITE",
            "name": name,
            "url": url,
            "domain": domain
        }

