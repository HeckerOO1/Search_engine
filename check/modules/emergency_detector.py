"""Emergency Mode Detection Module.

Detects when a search query is related to an emergency situation
and should switch from Standard Mode to Emergency Mode.
"""

import re
from config import EMERGENCY_KEYWORDS


def detect_emergency_mode(query: str) -> dict:
    """
    Analyze a search query to determine if it's emergency-related.
    
    Args:
        query: The user's search query
        
    Returns:
        dict with:
            - mode: "emergency" or "standard"
            - confidence: 0.0 to 1.0
            - triggers: list of matched emergency keywords
    """
    query_lower = query.lower()
    triggers = []
    
    # Check for emergency keywords
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in query_lower:
            triggers.append(keyword)
    
    # Check for urgency patterns
    urgency_patterns = [
        r'\b(now|urgent|immediately|asap|help)\b',
        r'\b(where to go|how to escape|safe place|nearest)\b',
        r'\b(warning|alert|danger|caution)\b',
        r'\b(breaking|live|current|latest)\b'
    ]
    
    urgency_count = 0
    for pattern in urgency_patterns:
        if re.search(pattern, query_lower):
            urgency_count += 1
    
    # Calculate confidence score
    keyword_score = min(len(triggers) * 0.3, 0.7)
    urgency_score = min(urgency_count * 0.15, 0.3)
    confidence = min(keyword_score + urgency_score, 1.0)
    
    # Determine mode
    if confidence >= 0.3 or len(triggers) > 0:
        mode = "emergency"
    else:
        mode = "standard"
    
    return {
        "mode": mode,
        "confidence": round(confidence, 2),
        "triggers": triggers
    }


def is_location_emergency(query: str, current_location: str = None) -> bool:
    """
    Check if the query mentions a location with an ongoing emergency.
    
    Args:
        query: The search query
        current_location: Optional current location context
        
    Returns:
        bool indicating if location-based emergency detected
    """
    location_emergency_patterns = [
        r'(earthquake|fire|flood|storm) (in|near|at) \w+',
        r'\w+ (earthquake|fire|flood|storm)',
        r'evacuation (in|near|from) \w+'
    ]
    
    for pattern in location_emergency_patterns:
        if re.search(pattern, query.lower()):
            return True
    
    return False
