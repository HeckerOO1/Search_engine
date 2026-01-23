"""Configuration settings for the Emergency Search Engine."""

import os
from dotenv import load_dotenv

load_dotenv()

# Emergency detection keywords
EMERGENCY_KEYWORDS = [
    "earthquake", "tsunami", "wildfire", "hurricane", "flood",
    "evacuation", "shelter", "emergency alert", "active shooter",
    "tornado warning", "amber alert", "disaster", "explosion",
    "fire", "storm", "cyclone", "emergency", "crisis", "rescue",
    "missing person", "accident", "collapse", "outbreak", "pandemic",
    "chemical spill", "gas leak", "power outage", "blackout"
]

# =====================================================
# SOURCE TRUST TIERS (ordered by credibility)
# =====================================================

# Tier 1: Official sources (government, education, military)
OFFICIAL_SOURCES = [
    ".gov", ".edu", ".mil",".org",
    "weather.gov", "noaa.gov", "fema.gov", "cdc.gov"
]

# Tier 2: Verified sources (established news agencies & organizations)
VERIFIED_SOURCES = [
    # Major news agencies
    "reuters.com", "apnews.com", 
    
    # International broadcasters
    "bbc.com", "bbc.co.uk",
    
    # Established newspapers
    "nytimes.com", "washingtonpost.com", "theguardian.com",
    
    # Broadcast news
    "cnn.com", "npr.org", "pbs.org",
    
    # International organizations
    "who.int", "redcross.org", "un.org"
]

# Tier 3: Semi-trusted sources (moderate credibility)
SEMI_TRUSTED_SOURCES = [
    # Mainstream media outlets
    "abc.com", "nbcnews.com", "cbsnews.com", "foxnews.com",
    "usatoday.com", "wsj.com", "bloomberg.com", "forbes.com",
    "time.com", "newsweek.com", "politico.com", "thehill.com",
    
    # International news
    "aljazeera.com", "france24.com", "dw.com", "scmp.com",
    "thetimes.co.uk", "independent.co.uk", "telegraph.co.uk",
    
    # Tech and science
    "scientificamerican.com", "nature.com", "sciencemag.org",
    "wired.com", "arstechnica.com", "theverge.com",
    
    # Regional/local news
    "latimes.com", "chicagotribune.com", "sfchronicle.com",
    "bostonglobe.com", "denverpost.com", "seattletimes.com",
    
    # Fact-checking
    "snopes.com", "factcheck.org", "politifact.com",
    
    # Health organizations
    "mayoclinic.org", "webmd.com", "healthline.com"
]

# Scoring weights (must sum to 1.0)
STANDARD_MODE_WEIGHTS = {
    "relevance": 0.30,    # How well query matches document
    "trust": 0.25,        # Source credibility
    "freshness": 0.15,    # Content recency
    "popularity": 0.20,   # Click-through rate
    "location": 0.10      # Geographic relevance
}

EMERGENCY_MODE_WEIGHTS = {
    "relevance": 0.20,    # Less critical in emergencies
    "trust": 0.25,        # Source credibility
    "freshness": 0.35,    # Recent info is critical
    "popularity": 0.05,   # Less important
    "location": 0.15      # Geographic relevance
}

# Behavior tracking settings
POGO_STICK_THRESHOLD_SECONDS = 5  # Quick return threshold
POGO_STICK_PENALTY = 0.3  # Score reduction for high bounce rate
MAX_POGO_COUNT_BEFORE_DEMOTE = 3  # Demote after this many quick returns
