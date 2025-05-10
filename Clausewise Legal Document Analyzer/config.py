import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Clause patterns
    CLAUSE_PATTERNS = {
        "confidentiality": r"(confidential|non[\s-]?disclosure|nda)",
        "termination": r"terminat",
        "indemnification": r"indemnif",
        "liability": r"(liability|limitation of liability)",
        "governing_law": r"(governing law|jurisdiction|venue)",
        "ip_ownership": r"(intellectual property|ip|ownership|patent|copyright)",
        "warranties": r"warrant(y|ies)",
        "assignment": r"assign",
        "notice": r"notice",
        "severability": r"severab",
        "force_majeure": r"force majeure",
        "arbitration": r"arbitrat",
        "auto_renewal": r"(auto[\s-]?renew|evergreen)"
    }
    
    RISK_KEYWORDS = {
        "high": ["irrevocable", "uncapped", "joint and several", "exclusive", "perpetual",'penalty', 'compensation', 'termination', '₹'],
        "medium": ["sole discretion", "without cause", "indemnify", "liquidated damages",'discretion', 'solely responsible', 'non-negotiable','non-refundable'],
        "low": ["reasonable efforts", "good faith", "mutual",'attempt', 'may be']
    }