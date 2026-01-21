"""Truth Filter Module.

Uses AI and heuristics to evaluate the trustworthiness of search results,
filtering out potential fake news and misinformation.
"""

import re
from urllib.parse import urlparse
from config import TRUSTED_SOURCES


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
    
    # Keyword stuffing detection (percentage-based)
    words = text.lower().split()
    total_words = len(words)
    
    if total_words > 0:
        # Filter out very short words (articles, conjunctions, etc.)
        meaningful_words = [w for w in words if len(w) > 3]
        
        if meaningful_words:
            # Count word frequencies
            word_counts = {}
            for word in meaningful_words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            # Check if any word exceeds 20% threshold
            for word, count in word_counts.items():
                percentage = (count / total_words) * 100
                if percentage > 20:
                    red_flags.append("keyword_stuffing")
                    break
    
    return {
        "red_flags": red_flags,
        "red_flag_count": len(red_flags),
        "is_suspicious": len(red_flags) >= 2
    }





def calculate_trust_score(result: dict) -> dict:
    """
    Calculate overall trust score for a search result.
    
    Args:
        result: Search result with 'title', 'snippet', 'link' keys
        
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
    penalty = 0
    for flag in misinfo["red_flags"]:
        if flag == "keyword_stuffing":
            penalty += 0.5  # Massive penalty for keyword stuffing
        else:
            penalty += 0.15  # Standard penalty for other red flags
    
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
