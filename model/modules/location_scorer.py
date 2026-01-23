"""Location Scoring Module.

Handles detection of locations in queries and matching them against search results.
"""

import json
import os
import re
from typing import Optional, List, Set

# Shared locations to detect
KNOWN_LOCATIONS = set()

# spaCy model cache
_nlp_model = None

def get_spacy_model():
    """Lazy load spaCy model and cache it."""
    global _nlp_model
    
    if _nlp_model is not None:
        return _nlp_model
    
    try:
        import spacy
        _nlp_model = spacy.load("en_core_web_sm")
        return _nlp_model
    except Exception as e:
        print(f"Warning: spaCy model not available: {e}")
        print("Install with: python -m spacy download en_core_web_sm")
        return None

def load_locations():
    """Load known locations from data.json to build a vocabulary."""
    global KNOWN_LOCATIONS
    try:
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.json')
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                data = json.load(f)
                mock_results = data.get("mock_search_results", [])
                for item in mock_results:
                    loc = item.get("location")
                    if loc:
                        # Add full location and parts (e.g., "California, USA" -> "California", "USA")
                        KNOWN_LOCATIONS.add(loc.lower())
                        for part in re.split(r'[,\s]+', loc):
                            if len(part) > 2: # Ignore short codes
                                KNOWN_LOCATIONS.add(part.lower())
        
        # Add some common manual ones just in case
        KNOWN_LOCATIONS.update(["bihar", "nepal", "india", "california", "texas", "japan", "turkey", "pakistan"])
    except Exception as e:
        print(f"Warning: Failed to load locations: {e}")

# Initial load
load_locations()

def detect_location_in_query_ner(query: str) -> Optional[str]:
    """
    Use NER (Named Entity Recognition) to detect locations in query.
    More intelligent than regex - understands context and multi-word locations.
    
    Args:
        query: User's search query
        
    Returns:
        Detected location string or None
    """
    nlp = get_spacy_model()
    if nlp is None:
        return None
    
    try:
        doc = nlp(query)
        
        # Extract GPE (Geo-Political Entity) locations
        locations = [(ent.text, ent.start) for ent in doc.ents if ent.label_ == "GPE"]
        
        if not locations:
            return None
        
        # If multiple locations, prefer one after location prepositions
        location_prepositions = {"in", "near", "at", "around", "from"}
        
        for loc_text, loc_start in locations:
            # Check tokens before the location
            if loc_start > 0:
                prev_token = doc[loc_start - 1].text.lower()
                if prev_token in location_prepositions:
                    return loc_text
        
        # Otherwise return first location found
        return locations[0][0]
    
    except Exception:
        return None

def detect_location_in_query_regex(query: str) -> Optional[str]:
    """
    Fallback regex-based location detection.
    Uses hardcoded KNOWN_LOCATIONS list.
    
    Args:
        query: User's search query
        
    Returns:
        Detected location string or None
    """
    query_lower = query.lower()
    # Sort by length descending to match longer strings first (e.g., "New York" before "York")
    sorted_locs = sorted(list(KNOWN_LOCATIONS), key=len, reverse=True)
    
    for loc in sorted_locs:
        # Use word boundaries to avoid partial matches (e.g., "man" in "manual")
        pattern = r'\b' + re.escape(loc) + r'\b'
        if re.search(pattern, query_lower):
            return loc
            
    return None

def detect_location_in_query(query: str) -> Optional[str]:
    """
    Detect location in query using NER (primary) with regex fallback.
    
    This hybrid approach provides:
    - NER: Intelligent context-aware detection, handles unknown locations
    - Regex: Reliable fallback if NER fails or model unavailable
    
    Args:
        query: User's search query
        
    Returns:
        The detected location string or None.
    """
    # Try NER first (more accurate)
    location = detect_location_in_query_ner(query)
    
    if location:
        return location
    
    # Fallback to regex (always works)
    return detect_location_in_query_regex(query)

def calculate_location_score(result: dict, target_location: str) -> float:
    """
    Calculate how well a result matches the target location.
    
    Args:
        result: The search result dictionary.
        target_location: The location detected in the query.
        
    Returns:
        Score between 0.0 and 1.0.
    """
    if not target_location:
        return 1.0 # Neutral if no location target
        
    # Check if result has a location field (for mock data)
    res_loc = result.get("location", "").lower()
    if target_location in res_loc or res_loc in target_location:
        return 1.0
        
    # Check title and snippet for real search results
    text = (result.get("title", "") + " " + result.get("snippet", "")).lower()
    if target_location in text:
        return 1.0
        
    # Partial match logic (if target is "California, USA", match "California")
    target_parts = re.split(r'[,\s]+', target_location)
    for part in target_parts:
        if len(part) > 3 and part in text:
            return 0.8
            
    return 0.1 # Low score if location doesn't match at all
