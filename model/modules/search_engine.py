"""Custom Search Module.

Two Modes:
1. Hybrid: Try external search (Google→Bing→Yahoo), fallback to local if all fail
2. Local-Only: Use URLs from data.json and scrape them for fresh content
"""

from typing import List, Dict, Optional
import time
import json
import os
import random
from modules.discovery import discovery_layer
from modules.scraper import scraper
from config import SEARCH_MODE

class SearchEngine:
    """End-to-end strict search engine."""
    
    def __init__(self):
        self.mock_data = []
        self._load_mock_data()

    def _load_mock_data(self):
        """Load fallback data from data.json"""
        try:
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.json')
            with open(data_path, 'r') as f:
                data = json.load(f)
                if "mock_search_results" in data:
                    self.mock_data = data["mock_search_results"]
                else:
                    self.mock_data = data if isinstance(data, list) else []
            print(f"Loaded {len(self.mock_data)} mock records for fallback.")
        except Exception as e:
            print(f"Warning: Could not load mock data: {e}")
            self.mock_data = []
    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL by removing fragments and query parameters.
        This prevents duplicates like:
        - https://en.wikipedia.org/wiki/Page
        - https://en.wikipedia.org/wiki/Page#section
        - https://en.wikipedia.org/wiki/Page?param=value
        """
        from urllib.parse import urlparse, urlunparse
        
        parsed = urlparse(url)
        # Remove fragment (#) and query (?)
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            '',  # params
            '',  # query
            ''   # fragment
        ))
        return normalized

    def search(self, query: str, num_results: int = 10, **kwargs) -> dict:
        """
        Execute search based on SEARCH_MODE configuration.
        """
        start_time = time.time()
        results = []
        source_used = "unknown"
        
        try:
            if SEARCH_MODE == "local_only":
                # LOCAL-ONLY MODE: Get URLs from data.json and scrape them
                print(f"[LOCAL-ONLY MODE] Searching local database and scraping URLs...")
                results = self._search_local_with_scraping(query, num_results)
                source_used = "local_database"
                
            else:
                # HYBRID MODE: Try external, fallback to local
                print(f"[HYBRID MODE] Attempting external search...")
                candidate_urls = discovery_layer.discover_urls(query, num_results=num_results)
                
                if candidate_urls:
                    # --- LIVE PATH ---
                    print(f"Discovery found {len(candidate_urls)} URLs. Proceeding to SCRAPE.")
                    source_used = "live"
                    
                    # PHASE 2: SCRAPING (with deduplication)
                    scraped_items = []
                    seen_urls = set()
                    
                    for url in candidate_urls:
                        # Normalize URL to prevent duplicates with different fragments/params
                        normalized_url = self._normalize_url(url)
                        
                        # Skip if we've already processed this normalized URL
                        if normalized_url in seen_urls:
                            print(f"Skipping duplicate: {url}")
                            continue
                        seen_urls.add(normalized_url)
                        
                        # Scrape using the original URL
                        item = scraper.scrape(url)
                        if item:
                            # Store normalized URL to ensure consistency
                            item['link'] = normalized_url
                            scraped_items.append(item)
                        # Soft rate limiting
                        time.sleep(0.3)
                    
                    # PHASE 3: PARSING & RANKING PREP
                    for item in scraped_items:
                        result = self._parse_scraped_item(item)
                        if result:
                            results.append(result)
                            
                    # Determine specific live source for UI
                    if results and "google" in results[0]["link"]: source_used = "google"
                    elif results and "bing.com" in results[0]["link"]: source_used = "bing"
                    elif results and "yahoo.com" in results[0]["link"]: source_used = "yahoo"
                    
                else:
                    # --- FALLBACK PATH ---
                    # Only entered if Discovery returned ZERO URLs
                    print("Discovery returned 0 URLs. Switching to EXCLUSIVE FALLBACK (Local Data).")
                    results = self._search_mock(query, num_results)
                    source_used = "database"

            search_time = time.time() - start_time
            
            message = None
            if source_used == "database":
                message = "Live search unavailable. Showing verified results from offline database."
            elif not results:
                message = "No results found."

            return {
                "results": results[:num_results],
                "total_results": len(results),
                "search_time": round(search_time, 2),
                "query": query,
                "error": None,
                "message": message,
                "source": source_used, # 'live', 'brave', 'database', etc.
                "mode": kwargs.get("mode", "standard")
            }
                
        except Exception as e:
            print(f"Critical Search Error: {e}. Defaulting to Database.")
            return {
                "results": self._search_mock(query, num_results),
                "total_results": 0,
                "search_time": round(time.time() - start_time, 2),
                "query": query,
                "error": str(e),
                "source": "error_fallback",
                "message": "System error. Using offline mode."
            }

    def _parse_scraped_item(self, item: dict) -> dict:
        """Transform raw scraped item into search result format."""
        link = item.get("link", "")
        display_link = link.replace("https://", "").replace("http://", "").split('/')[0]
        
        return {
            "title": item.get("title", ""),
            "link": link,
            "snippet": item.get("snippet", ""),
            "content": item.get("content", ""),
            "displayLink": display_link,
            "pagemap": {},
            # Scoring placeholders (filled in by app.py's rank_results)
            "trust_score": 0,
            "freshness_score": 0,
            "final_score": 0,
            "badge": "unverified",
            "freshness_label": "unknown",
            "timestamp": item.get("timestamp")
        }

    def _search_local_with_scraping(self, query: str, num_results: int = 10) -> list:
        """
        LOCAL-ONLY MODE: Search data.json for matching entries and scrape their URLs.
        This provides fresh content from local URLs instead of using stored snippets.
        """
        query_terms = query.lower().split()
        matched_items = []
        
        # Find matching items in local data
        for item in self.mock_data:
            text = (item.get("title", "") + " " + item.get("content", "") + " " + " ".join(item.get("keywords", []))).lower()
            
            score = 0
            for term in query_terms:
                if term in text:
                    score += 1
            
            if score > 0:
                matched_items.append((score, item))
        
        # Sort by relevance
        matched_items.sort(key=lambda x: x[0], reverse=True)
        
        # Scrape URLs from matched items
        results = []
        seen_urls = set()
        
        for score, item in matched_items[:num_results * 2]:  # Get more to account for scraping failures
            url = item.get("source", "")
            
            # Skip if no URL or already processed
            if not url or url == "#" or not url.startswith("http"):
                continue
            
            normalized_url = self._normalize_url(url)
            if normalized_url in seen_urls:
                continue
            seen_urls.add(normalized_url)
            
            # Scrape the URL for fresh content
            print(f"[LOCAL-ONLY] Scraping: {url}")
            scraped = scraper.scrape(url)
            
            if scraped:
                scraped['link'] = normalized_url
                result = self._parse_scraped_item(scraped)
                if result:
                    results.append(result)
                    if len(results) >= num_results:
                        break
            
            time.sleep(0.3)  # Rate limiting
        
        # If scraping didn't get enough results, fill with stored data
        if len(results) < num_results:
            print(f"[LOCAL-ONLY] Scraping got {len(results)} results, filling with stored data...")
            for score, item in matched_items:
                if len(results) >= num_results:
                    break
                # Check if we already have this URL
                url = self._normalize_url(item.get("source", ""))
                if url not in seen_urls:
                    results.append(self._parse_mock_result(item))
        
        return results[:num_results]


    def _search_mock(self, query: str, num_results: int = 10) -> list:
        """Search local mock data as strict fallback."""
        query_terms = query.lower().split()
        results = []
        
        for item in self.mock_data:
            # searchable text: title + content + keywords
            text = (item.get("title", "") + " " + item.get("content", "") + " " + " ".join(item.get("keywords", []))).lower()
            
            # Simple scoring for fallback
            score = 0
            for term in query_terms:
                if term in text:
                    score += 1
            
            if score > 0:
                res = self._parse_mock_result(item)
                # Store temporary score for sorting
                res["_temp_score"] = score
                results.append(res)
                
        # Sort by simple keyword match count
        results.sort(key=lambda x: x["_temp_score"], reverse=True)
        
        # Remove temp score before returning
        for r in results:
            del r["_temp_score"]
            
        return results[:num_results]

    def _parse_mock_result(self, item: dict) -> dict:
        """Parse local JSON item into standard result format."""
        return {
            "title": item.get("title", "No Title"),
            "link": item.get("source", "#"),
            "snippet": item.get("content", ""),
            "content": item.get("content", ""),
            "displayLink": "Verified Database",
            "trust_score": item.get("trust", 0.9), # High trust for curated data
            "freshness_score": 0.5, # Mid freshness for static data
            "final_score": 0,
            "badge": "verified", # Always verified
            "freshness_label": "archived",
            "location": item.get("location", "")
        }

    def search_emergency(self, query: str, num_results: int = 10) -> dict:
        """
        Emergency search. 
        In strict mode, we use the same pipeline but the App layer will apply different Ranking weights.
        """
        return self.search(query, num_results=num_results, mode="emergency")


# Singleton instance
search_engine = SearchEngine()
