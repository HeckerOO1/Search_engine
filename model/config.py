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

# Trusted source domains for Truth Filter
TRUSTED_SOURCES = [
    ".gov", ".edu", ".mil",
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
    "nytimes.com", "washingtonpost.com", "theguardian.com",
    "cnn.com", "npr.org", "pbs.org",
    "weather.gov", "noaa.gov", "fema.gov", "cdc.gov",
    "who.int", "redcross.org", "un.org"
]

# Scoring weights
STANDARD_MODE_WEIGHTS = {
    "freshness": 0.2,
    "trust": 0.3,
    "popularity": 0.5
}

EMERGENCY_MODE_WEIGHTS = {
    "freshness": 0.5,
    "trust": 0.4,
    "popularity": 0.1
}

# Behavior tracking settings
POGO_STICK_THRESHOLD_SECONDS = 5  # Quick return threshold
POGO_STICK_PENALTY = 0.3  # Score reduction for high bounce rate
MAX_POGO_COUNT_BEFORE_DEMOTE = 3  # Demote after this many quick returns
