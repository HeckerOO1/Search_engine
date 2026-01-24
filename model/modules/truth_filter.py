"""Truth Filter Module.

Uses AI and heuristics to evaluate the trustworthiness of search results,
filtering out potential fake news and misinformation.
"""

import re
from urllib.parse import urlparse
from config import OFFICIAL_SOURCES, VERIFIED_SOURCES, SEMI_TRUSTED_SOURCES


def get_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return ""


def check_trusted_source(url: str) -> tuple:
    """
    Check source tier by matching against three separate lists.
    
    Detection Priority:
    1. OFFICIAL_SOURCES → "official" (0.95)
    2. VERIFIED_SOURCES → "verified" (0.8)
    3. SEMI_TRUSTED_SOURCES → "semi-trusted" (0.6)
    4. Everything else → "unknown" (0.4)
    
    Returns:
        tuple: (is_trusted: bool, trust_level: str)
    """
    domain = get_domain(url)
    
    # Tier 1: Check OFFICIAL_SOURCES (.gov, .edu, .mil)
    for official in OFFICIAL_SOURCES:
        if official in domain:
            return (True, "official")
    
    # Tier 2: Check VERIFIED_SOURCES (Reuters, BBC, NYT, etc.)
    for verified in VERIFIED_SOURCES:
        if verified in domain:
            return (True, "verified")
    
    # Tier 3: Check SEMI_TRUSTED_SOURCES (NBC, Forbes, etc.)
    for semi_trusted in SEMI_TRUSTED_SOURCES:
        if semi_trusted in domain:
            return (False, "semi-trusted")
    
    # Tier 4: Unknown sources
    return (False, "unknown")


def detect_misinformation_patterns(title: str, snippet: str) -> dict:
    """
    Detect common misinformation patterns in content.
    Analyzes title and snippet separately with weighted penalties.
    
    Title: 60% weight, penalty starts at 1+ matches
    Snippet: 40% weight, penalty starts at 2+ matches
    
    Returns:
        dict with pattern analysis results
    """
    # Pattern definitions (all patterns we want to count)
    all_patterns = {
        "sensationalist": [
            r'\b(shocking|unbelievable|you won\'t believe|secret|they don\'t want you to know)\b',
            r'\b(miracle|cure-all|100% guaranteed)\b',
        ],
        "unverified": [
            r'\b(sources say|reportedly|allegedly|rumor|unconfirmed)\b',
            r'\b(viral|spreading|everyone is saying)\b'
        ],
        "fear_mongering": [
            r'\b(doom|catastrophe|end of|apocalypse|collapse)\b',
            r'\b(panic|terrifying|horrifying)\b'
        ]
    }
    
    # Special patterns for title only
    title_special = [
        r'^[A-Z\s!]{10,}',  # ALL CAPS headlines
        r'!{2,}',  # Multiple exclamation marks
    ]
    
    red_flags = []
    
    # ===== TITLE ANALYSIS (60% weight) =====
    title_lower = title.lower()
    title_match_count = 0
    
    # Count pattern word matches in title
    for category, patterns in all_patterns.items():
        for pattern in patterns:
            matches = re.findall(pattern, title_lower)
            title_match_count += len(matches)
    
    # Check special title patterns (count as 1 match each if found)
    for pattern in title_special:
        if re.search(pattern, title):
            title_match_count += 1
    
    # Calculate title penalty
    title_penalty = 0
    if title_match_count >= 1:
        # Base: 0.15 for first match, +0.05 for each additional
        title_penalty = 0.15 + (max(0, title_match_count - 1) * 0.05)
        red_flags.append(f"title_spam_{title_match_count}x")
    
    # ===== SNIPPET ANALYSIS (40% weight) =====
    snippet_lower = snippet.lower()
    snippet_match_count = 0
    
    # Count pattern word matches in snippet
    for category, patterns in all_patterns.items():
        for pattern in patterns:
            matches = re.findall(pattern, snippet_lower)
            snippet_match_count += len(matches)
    
    # Calculate snippet penalty
    snippet_penalty = 0
    if snippet_match_count >= 2:
        # Base: 0.1 for 2 matches, +0.05 for each additional
        snippet_penalty = 0.1 + (max(0, snippet_match_count - 2) * 0.05)
        red_flags.append(f"snippet_spam_{snippet_match_count}x")
    
    #  COMBINED WEIGHTED PENALTY 
    pattern_penalty = (title_penalty * 0.6) + (snippet_penalty * 0.4)
    
    #  KEYWORD STUFFING (on combined text) 
    combined_text = f"{title_lower} {snippet_lower}"
    words = combined_text.split()
    total_words = len(words)
    
    keyword_stuffing_penalty = 0
    if total_words > 0:
        # Filter out very short words
        meaningful_words = [w for w in words if len(w) > 3]
        
        if meaningful_words:
            word_counts = {}
            for word in meaningful_words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            # Check if any word exceeds 20% threshold
            for word, count in word_counts.items():
                percentage = (count / total_words) * 100
                if percentage > 20:
                    keyword_stuffing_penalty = 0.5
                    red_flags.append("keyword_stuffing")
                    break
    
    #  FINAL RESULTS 
    total_penalty = pattern_penalty + keyword_stuffing_penalty
    
    return {
        "red_flags": red_flags,
        "title_matches": title_match_count,
        "snippet_matches": snippet_match_count,
        "title_penalty": round(title_penalty, 3),
        "snippet_penalty": round(snippet_penalty, 3),
        "pattern_penalty": round(pattern_penalty, 3),
        "keyword_stuffing_penalty": keyword_stuffing_penalty,
        "total_penalty": round(total_penalty, 3),
        "is_suspicious": total_penalty >= 0.3
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
    
    # Calculate base score based on trust tier
    if trust_level == "official":
        base_score = 0.95
    elif trust_level == "verified":
        base_score = 0.8
    elif trust_level == "semi-trusted":
        base_score = 0.6
    else:  # unknown
        base_score = 0.4
    
    # Apply penalty from misinformation detection
    # The penalty is already calculated with weighted scores in detect_misinformation_patterns
    penalty = misinfo["total_penalty"]
    
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
