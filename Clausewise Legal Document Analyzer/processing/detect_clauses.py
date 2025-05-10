import re
import spacy
from config import Config

nlp = spacy.load("en_core_web_sm")

class ClauseDetector:
    def __init__(self):
        self.patterns = Config.CLAUSE_PATTERNS

    def detect_clauses(self, text: str) -> list[dict]:
        """Identify clauses using regex and NLP"""
        # First pass with regex
        clauses = []
        for clause_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                clauses.append({
                    "type": clause_type,
                    "start": match.start(),
                    "end": match.end(),
                    "text": self._expand_to_full_clause(text, match.start(), match.end())
                })
        
        # Sort by position
        clauses.sort(key=lambda x: x["start"])
        
        return clauses

    def _expand_to_full_clause(self, text: str, start: int, end: int) -> str:
        """Expand match to full clause using NLP"""
        # Get surrounding 500 characters for context
        context_start = max(0, start - 250)
        context_end = min(len(text), end + 250)
        context = text[context_start:context_end]
        
        # Use spaCy to find sentence boundaries
        doc = nlp(context)
        sentences = [sent.text for sent in doc.sents]
        
        # Find which sentence contains our match
        match_text = text[start:end]
        for sent in sentences:
            if match_text in sent:
                return sent.strip()
        
        return text[start:end]  # Fallback to original match