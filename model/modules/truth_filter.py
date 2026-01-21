"""Truth Filter Module.

Uses AI and heuristics to evaluate the trustworthiness of search results,
filtering out potential fake news and misinformation.
"""

import re
from urllib.parse import urlparse
from config import TRUSTED_SOURCES, GEMINI_API_KEY

# Try to import Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = bool(GEMINI_API_KEY)
    if GEMINI_AVAILABLE:
        genai.configure(api_key=GEMINI_API_KEY)
except ImportError:
    GEMINI_AVAILABLE = False


def get_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return ""


def check_trusted_source(url: str) -> tuple:
    """
    Check if URL is from a trusted source.
    
    Returns:
        tuple: (is_trusted: bool, trust_level: str)
    """
    domain = get_domain(url)
    
    for trusted in TRUSTED_SOURCES:
        if trusted in domain:
            # Government and official sources get highest trust
            if trusted in ['.gov', '.edu', '.mil']:
                return (True, "official")
            else:
                return (True, "verified")
    
    return (False, "unverified")


def detect_misinformation_patterns(title: str, snippet: str) -> dict:
    """
    Detect common misinformation patterns in content.
    
    Returns:
        dict with pattern analysis results
    """
    text = f"{title} {snippet}".lower()
    
    red_flags = []
    
    # Sensationalist patterns
    sensationalist_patterns = [
        r'\b(shocking|unbelievable|you won\'t believe|secret|they don\'t want you to know)\b',
        r'\b(miracle|cure-all|100% guaranteed)\b',
        r'^[A-Z\s!]{10,}',  # ALL CAPS headlines
        r'!{2,}',  # Multiple exclamation marks
    ]
    
    for pattern in sensationalist_patterns:
        if re.search(pattern, text):
            red_flags.append("sensationalist_language")
            break
    
    # Unverified claim patterns
    unverified_patterns = [
        r'\b(sources say|reportedly|allegedly|rumor|unconfirmed)\b',
        r'\b(viral|spreading|everyone is saying)\b'
    ]
    
    for pattern in unverified_patterns:
        if re.search(pattern, text):
            red_flags.append("unverified_claims")
            break
    
    # Fear-mongering patterns
    fear_patterns = [
        r'\b(doom|catastrophe|end of|apocalypse|collapse)\b',
        r'\b(panic|terrifying|horrifying)\b'
    ]
    
    for pattern in fear_patterns:
        if re.search(pattern, text):
            red_flags.append("fear_mongering")
            break
    
    return {
        "red_flags": red_flags,
        "red_flag_count": len(red_flags),
        "is_suspicious": len(red_flags) >= 2
    }


async def analyze_with_ai(title: str, snippet: str, url: str) -> dict:
    """
    Use Gemini AI to analyze content trustworthiness.
    """
    if not GEMINI_AVAILABLE:
        return {"ai_score": 0.5, "ai_analysis": "AI analysis unavailable"}
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Analyze this search result for trustworthiness during an emergency situation.
Rate from 0 (fake/unreliable) to 1 (trustworthy/reliable).
Consider: source credibility, factual language, official information patterns.

Title: {title}
Snippet: {snippet}
URL: {url}

Respond with ONLY a JSON object: {{"score": 0.X, "reason": "brief explanation"}}"""
        
        response = await model.generate_content_async(prompt)
        
        # Parse response
        import json
        result = json.loads(response.text)
        return {
            "ai_score": result.get("score", 0.5),
            "ai_analysis": result.get("reason", "")
        }
    except Exception as e:
        return {"ai_score": 0.5, "ai_analysis": f"AI analysis error: {str(e)}"}


def calculate_trust_score(result: dict, use_ai: bool = False) -> dict:
    """
    Calculate overall trust score for a search result.
    
    Args:
        result: Search result with 'title', 'snippet', 'link' keys
        use_ai: Whether to use AI analysis (slower but more accurate)
        
    Returns:
        dict with trust score and details
    """
    title = result.get("title", "")
    snippet = result.get("snippet", "")
    url = result.get("link", "")
    
    # Check trusted source
    is_trusted, trust_level = check_trusted_source(url)
    
    # Detect misinformation patterns
    misinfo = detect_misinformation_patterns(title, snippet)
    
    # Calculate base score
    if trust_level == "official":
        base_score = 0.95
    elif trust_level == "verified":
        base_score = 0.8
    else:
        base_score = 0.5
    
    # Apply penalties for red flags
    penalty = misinfo["red_flag_count"] * 0.15
    final_score = max(0.1, base_score - penalty)
    
    # Determine badge
    if final_score >= 0.8:
        badge = "verified"
    elif final_score >= 0.5:
        badge = "unverified"
    else:
        badge = "suspicious"
    
    return {
        "trust_score": round(final_score, 2),
        "trust_level": trust_level,
        "badge": badge,
        "is_trusted_source": is_trusted,
        "red_flags": misinfo["red_flags"],
        "is_suspicious": misinfo["is_suspicious"]
    }
