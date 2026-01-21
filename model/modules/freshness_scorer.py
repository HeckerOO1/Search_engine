"""Freshness Scoring Module.

Evaluates how recent content is and assigns freshness scores.
In emergency mode, recent content is heavily prioritized.
"""

import re
from datetime import datetime, timedelta
from typing import Optional


def parse_date_from_snippet(snippet: str) -> Optional[datetime]:
    """
    Try to extract a date from the snippet text.
    
    Returns:
        datetime if found, None otherwise
    """
    # Common date patterns
    patterns = [
        # "Jan 21, 2026" or "January 21, 2026"
        r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{1,2}),?\s+(\d{4})',
        # "21 Jan 2026"
        r'(\d{1,2})\s+(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{4})',
        # "2026-01-21"
        r'(\d{4})-(\d{2})-(\d{2})',
        # Relative: "X hours ago", "X minutes ago"
        r'(\d+)\s+(minute|hour|day|week)s?\s+ago',
    ]
    
    month_map = {
        'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
        'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
        'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
        'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
        'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }
    
    text = snippet.lower()
    
    # Check for relative time
    relative_match = re.search(r'(\d+)\s+(minute|hour|day|week)s?\s+ago', text)
    if relative_match:
        amount = int(relative_match.group(1))
        unit = relative_match.group(2)
        now = datetime.now()
        
        if unit == 'minute':
            return now - timedelta(minutes=amount)
        elif unit == 'hour':
            return now - timedelta(hours=amount)
        elif unit == 'day':
            return now - timedelta(days=amount)
        elif unit == 'week':
            return now - timedelta(weeks=amount)
    
    # Check for "Month Day, Year" pattern
    match = re.search(patterns[0], snippet, re.IGNORECASE)
    if match:
        month = month_map.get(match.group(1).lower()[:3], 1)
        day = int(match.group(2))
        year = int(match.group(3))
        try:
            return datetime(year, month, day)
        except:
            pass
    
    # Check for ISO date format
    match = re.search(patterns[2], snippet)
    if match:
        try:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            return datetime(year, month, day)
        except:
            pass
    
    return None


def calculate_freshness_score(result: dict, is_emergency: bool = False) -> dict:
    """
    Calculate freshness score for a search result.
    
    Args:
        result: Search result with potential date information
        is_emergency: If True, apply stricter freshness requirements
        
    Returns:
        dict with freshness score and metadata
    """
    now = datetime.now()
    
    # Try to get date from metatags or snippet
    snippet = result.get("snippet", "")
    title = result.get("title", "")
    
    # Check for date in page metadata
    pagemap = result.get("pagemap", {})
    metatags = pagemap.get("metatags", [{}])[0] if pagemap.get("metatags") else {}
    
    article_date = None
    
    # Try common metadata fields
    date_fields = [
        "article:published_time",
        "og:updated_time",
        "datePublished",
        "dateModified",
        "date"
    ]
    
    for field in date_fields:
        if metatags.get(field):
            try:
                date_str = metatags[field]
                # Parse ISO format
                article_date = datetime.fromisoformat(date_str.replace('Z', '+00:00').split('+')[0])
                break
            except:
                continue
    
    # Fall back to snippet parsing
    if not article_date:
        article_date = parse_date_from_snippet(f"{title} {snippet}")
    
    # Calculate score based on age
    if article_date:
        age = now - article_date
        age_hours = age.total_seconds() / 3600
        
        if is_emergency:
            # Emergency mode: very aggressive freshness decay
            if age_hours <= 1:
                score = 1.0
            elif age_hours <= 6:
                score = 0.9
            elif age_hours <= 24:
                score = 0.7
            elif age_hours <= 72:  # 3 days
                score = 0.4
            elif age_hours <= 168:  # 1 week
                score = 0.2
            else:
                score = 0.1
            
            freshness_label = get_freshness_label(age_hours, is_emergency=True)
        else:
            # Standard mode: gradual freshness decay
            if age_hours <= 24:
                score = 1.0
            elif age_hours <= 168:  # 1 week
                score = 0.8
            elif age_hours <= 720:  # 1 month
                score = 0.6
            elif age_hours <= 2160:  # 3 months
                score = 0.4
            else:
                score = 0.3
            
            freshness_label = get_freshness_label(age_hours, is_emergency=False)
        
        return {
            "freshness_score": round(score, 2),
            "publish_date": article_date.isoformat(),
            "age_hours": round(age_hours, 1),
            "freshness_label": freshness_label,
            "date_found": True
        }
    else:
        # No date found - assign neutral score
        return {
            "freshness_score": 0.5 if not is_emergency else 0.3,
            "publish_date": None,
            "age_hours": None,
            "freshness_label": "unknown",
            "date_found": False
        }


def get_freshness_label(age_hours: float, is_emergency: bool) -> str:
    """Get human-readable freshness label."""
    if age_hours <= 1:
        return "just now"
    elif age_hours <= 6:
        return "very recent"
    elif age_hours <= 24:
        return "today"
    elif age_hours <= 48:
        return "yesterday"
    elif age_hours <= 168:
        return "this week"
    elif age_hours <= 720:
        return "this month"
    else:
        if is_emergency:
            return "outdated"
        return "older"
