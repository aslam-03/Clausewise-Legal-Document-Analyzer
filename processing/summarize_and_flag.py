import google.generativeai as genai
from config import Config
import re
import json
import time
from typing import Dict, Any, Tuple
import logging
from typing import Dict, Any, Tuple, List
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

class ClauseAnalyzer:
    # Track last API call time for rate limiting
    LAST_API_CALL_TIME = 0
    MIN_CALL_INTERVAL = 1.0  # Minimum seconds between API calls

    @staticmethod
    def analyze_clause(clause_text: str) -> Dict[str, Any]:
        """Analyze clause with Gemini and risk detection"""
        if not clause_text.strip():
            return ClauseAnalyzer._empty_response("Empty clause text")

        try:
            # Get LLM analysis with rate limiting
            llm_response = ClauseAnalyzer._get_llm_analysis(clause_text)
            
            # Detect risk level
            risk_level, risk_reasons = ClauseAnalyzer._detect_risk(clause_text)
            
            return {
                "type": llm_response.get("Clause Type", "Unknown"),
                "summary": llm_response.get("Summary", ""),
                "risk_level": risk_level,
                "risk_reasons": risk_reasons
            }
        except Exception as e:
            logger.error(f"Error analyzing clause: {e}")
            return ClauseAnalyzer._empty_response(f"Analysis error: {str(e)}")

    @staticmethod
    def _empty_response(message: str) -> Dict[str, Any]:
        """Return a default error response"""
        return {
            "type": "Error",
            "summary": message,
            "risk_level": "none",
            "risk_reasons": []
        }

    @staticmethod
    def _get_llm_analysis(clause_text: str) -> Dict[str, Any]:
        """Get clause analysis from Gemini with rate limiting"""
        try:
            # Enforce rate limiting
            ClauseAnalyzer._enforce_rate_limit()
            
            prompt = ClauseAnalyzer._create_analysis_prompt(clause_text)
            response = model.generate_content(prompt)
            return ClauseAnalyzer._parse_response(response.text)
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                logger.warning("Hit rate limit, waiting 5 seconds...")
                time.sleep(5)
                return ClauseAnalyzer._get_llm_analysis(clause_text)  # Retry
            raise

    @staticmethod
    def _enforce_rate_limit():
        """Ensure we don't exceed API rate limits"""
        elapsed = time.time() - ClauseAnalyzer.LAST_API_CALL_TIME
        if elapsed < ClauseAnalyzer.MIN_CALL_INTERVAL:
            sleep_time = ClauseAnalyzer.MIN_CALL_INTERVAL - elapsed
            time.sleep(sleep_time)
        ClauseAnalyzer.LAST_API_CALL_TIME = time.time()

    @staticmethod
    def _create_analysis_prompt(clause_text: str) -> str:
        """Create the prompt for clause analysis"""
        return f"""Analyze this legal clause and respond in pure JSON format only:
{clause_text}

Required JSON structure:
{{
    "Clause Type": "[type]",
    "Summary": "[plain English summary]",
    "Risk Factors": ["list", "of", "risks"]
}}

Important:
1. Only return valid JSON
2. Keep summaries concise (1-2 sentences)
3. Focus on practical business implications
4. Highlight unusual or one-sided terms"""

    @staticmethod
    def _parse_response(response_text: str) -> Dict[str, Any]:
        """Robust parsing of Gemini response"""
        try:
            # Clean the response text
            cleaned_text = ClauseAnalyzer._clean_response_text(response_text)
            
            # Handle malformed JSON
            if not cleaned_text.startswith('{'):
                cleaned_text = '{' + cleaned_text.split('{', 1)[-1]
            if not cleaned_text.endswith('}'):
                cleaned_text = cleaned_text.rsplit('}', 1)[0] + '}'
                
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nOriginal response: {response_text}")
            # Fallback to extracting just the summary
            return {
                "Clause Type": "Unknown",
                "Summary": ClauseAnalyzer._extract_summary_from_response(response_text),
                "Risk Factors": []
            }

    @staticmethod
    def _clean_response_text(text: str) -> str:
        """Clean the API response text"""
        # Remove markdown code blocks
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        return text.strip()

    @staticmethod
    def _extract_summary_from_response(text: str) -> str:
        """Fallback method to extract summary from malformed response"""
        # Look for obvious summary patterns
        if '"Summary":' in text:
            parts = text.split('"Summary":')
            if len(parts) > 1:
                summary_part = parts[1].split('"', 2)
                if len(summary_part) > 2:
                    return summary_part[1]
        
        # Default to first 200 characters
        return text[:200].strip()

    @staticmethod
    def _detect_risk(clause_text: str) -> Tuple[str, List[str]]:
        """Detect risk level based on keywords and patterns"""
        reasons = []
        risk_level = "none"
        
        # Check for risk keywords from config
        for level, keywords in Config.RISK_KEYWORDS.items():
            for keyword in keywords:
                if re.search(rf"\b{re.escape(keyword)}\b", clause_text, re.IGNORECASE):
                    reasons.append(f"Contains '{keyword}'")
                    if risk_level == "none" or level == "high":
                        risk_level = level
        
        return risk_level, reasons