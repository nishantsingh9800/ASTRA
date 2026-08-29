import re
from typing import Dict, Any, Tuple, List, Optional
from packages.core.models import ConfidenceLevel, Entity, EntityType
from packages.core import logger

class EntityResolver:
    """
    General name/entity resolution system.
    Resolves STT phonetic errors for Indian names against local vocabularies.
    """
    def __init__(self):
        # Fetch dynamic local personal vocabulary from ContactProvider
        from packages.core.contact_provider import ContactProvider
        provider = ContactProvider()
        self.local_contacts = [contact["name"] for contact in provider.get_contacts()]
        
        self.local_projects = ["Astra", "Gemini", "Alpha"]
        self.local_projects = ["Astra", "Gemini", "Alpha"]
        
        # Action keywords that strongly suggest a PERSON entity follows
        self.person_actions = ["message", "call", "find", "search for", "text", "email"]
        
    def _levenshtein(self, s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def _generate_candidates(self, word: str, vocabulary: List[str], max_distance: int = 2) -> List[Tuple[str, int]]:
        candidates = []
        word_lower = word.lower()
        for item in vocabulary:
            # We match against the first name or the full name
            parts = item.split()
            for part in parts + [item]:
                dist = self._levenshtein(word_lower, part.lower())
                if dist <= max_distance:
                    candidates.append((item, dist))
        
        # Sort by distance
        candidates.sort(key=lambda x: x[1])
        # Deduplicate preserving order
        seen = set()
        deduped = []
        for c in candidates:
            if c[0] not in seen:
                seen.add(c[0])
                deduped.append(c)
        return deduped

    def resolve(self, text: str, context: Dict[str, Any]) -> Tuple[List[Entity], str, ConfidenceLevel, Optional[str]]:
        """
        Scans text for entities, performs phonetic matching, and returns:
        (resolved_entities, updated_text, resolution_confidence, clarification_question)
        """
        words = text.split()
        updated_words = list(words)
        resolved_entities = []
        clarification_question = None
        overall_confidence = ConfidenceLevel.HIGH

        for i, word in enumerate(words):
            # Clean punctuation for matching
            clean_word = re.sub(r'[^\w\s]', '', word)
            if not clean_word or clean_word.lower() in ["the", "a", "an", "to", "on", "in", "for"]:
                continue
                
            # Check context to see if this word follows a strong PERSON action
            is_person_context = False
            if i > 0:
                prev_phrase = " ".join(words[max(0, i-2):i]).lower()
                for action in self.person_actions:
                    if action in prev_phrase:
                        is_person_context = True
                        break
                        
            # Determine dynamic distance based on word length and context
            base_distance = 1
            if is_person_context:
                base_distance = 2
                if len(clean_word) > 5:
                    base_distance = 3
                    
            # Generate candidates from contacts
            candidates = self._generate_candidates(clean_word, self.local_contacts, max_distance=base_distance)
            
            if candidates:
                # Top candidate
                best_match, distance = candidates[0]
                
                # If distance is 0, exact match
                if distance == 0:
                    resolved_entities.append(Entity(
                        entity_type=EntityType.PERSON,
                        text=clean_word,
                        resolved_name=best_match,
                        confidence="HIGH",
                        source="Contacts"
                    ))
                    updated_words[i] = best_match
                else:
                    # If there's an ambiguity (multiple candidates with same distance)
                    if len(candidates) > 1 and candidates[0][1] == candidates[1][1]:
                        # Ambiguous!
                        overall_confidence = ConfidenceLevel.LOW
                        clarification_question = f"Did you mean {candidates[0][0]} or {candidates[1][0]}?"
                        logger.debug(f"[EntityResolver] Ambiguous match for '{clean_word}': {candidates}")
                        break
                    else:
                        # Single clear winner despite distance
                        if is_person_context or distance <= 1:
                            resolved_entities.append(Entity(
                                entity_type=EntityType.PERSON,
                                text=clean_word,
                                resolved_name=best_match,
                                confidence="HIGH" if is_person_context else "MEDIUM",
                                source="Contacts (Phonetic)"
                            ))
                            updated_words[i] = best_match
                            logger.debug(f"[EntityResolver] Phonetically resolved '{clean_word}' to '{best_match}'")
                            
        updated_text = " ".join(updated_words)
        return resolved_entities, updated_text, overall_confidence, clarification_question
