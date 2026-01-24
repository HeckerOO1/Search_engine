# all the settings and config stuff for the search engine

import os
from dotenv import load_dotenv

load_dotenv()

# =====================================================
# SEARCH MODE SETUP
# =====================================================
# you can pick "hybrid" or "local_only"
# hybrid = tries google/bing/yahoo first, falls back to local database if they all fail
# local_only = just uses the URLs from data.json and scrapes em
SEARCH_MODE = "hybrid"  # change this if you want different mode

# words that trigger emergency mode
# if user searches for these, we prioritize fresh info and trusted sources
EMERGENCY_KEYWORDS = [
    "earthquake", "tsunami", "wildfire", "hurricane", "flood",
    "evacuation", "shelter", "emergency alert", "active shooter",
    "tornado warning", "amber alert", "disaster", "explosion",
    "fire", "storm", "cyclone", "emergency", "crisis", "rescue",
    "missing person", "accident", "collapse", "outbreak", "pandemic",
    "chemical spill", "gas leak", "power outage", "blackout"
]

# =====================================================
# HOW MUCH WE TRUST DIFFERENT SOURCES
# =====================================================

# tier 1: government and education sites - these are super trustworthy
OFFICIAL_SOURCES = [
    ".gov", ".edu", ".mil",".org","usgs.gov",
    "weather.gov", "noaa.gov", "fema.gov", "cdc.gov"
]

# tier 2: verified news sites - pretty reliable but not as official
VERIFIED_SOURCES = [
    # big news agencies
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

# tier 3: semi-trusted - ok but not amazing
SEMI_TRUSTED_SOURCES = [
    # mainstream media
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

# how much weight we give to different factors when ranking results
# these gotta add up to 1.0
STANDARD_MODE_WEIGHTS = {
    "relevance": 0.30,    # how well it matches what user searched for
    "trust": 0.25,        # is the source reliable
    "freshness": 0.15,    # how recent is the info
    "popularity": 0.20,   # how many people click it
    "location": 0.10      # does it match the location user wants
}

# for emergency mode we care more about fresh info and less about popularity
EMERGENCY_MODE_WEIGHTS = {
    "relevance": 0.20,    # still matters but not as much
    "trust": 0.25,        # gotta be trustworthy in emergencies
    "freshness": 0.35,    # THIS IS SUPER IMPORTANT - need latest info
    "popularity": 0.05,   # dont really care about clicks in emergency
    "location": 0.15      # location matters more in emergencies
}

# pogo-sticking settings (when people bounce back quickly from a result)
POGO_STICK_THRESHOLD_SECONDS = 5  # if they come back in less than 5 sec, thats a pogo
POGO_STICK_PENALTY = 0.3  # how much we reduce the score
MAX_POGO_COUNT_BEFORE_DEMOTE = 3  # after 3 pogos we really demote it
ENABLE_LOCAL_SEARCH = False # set true if you want to search local database
ENABLE_EXTERNAL_SEARCH = True # set true to mix local with google/brave results
