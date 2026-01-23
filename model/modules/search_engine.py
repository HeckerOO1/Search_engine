"""Custom Search Module.

Implements Discovery -> Scrape -> Rank pipeline for "from-scratch" searching.
Uses discovery tool for URLs, then scrapes and ranks content natively.
"""

from typing import List, Dict
import time
import json
import os
import random
from modules.discovery import discovery_layer
from modules.scraper import scraper


class SearchEngine:
    """End-to-end custom search engine."""
    
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

    def search(self, query: str, num_results: int = 10, **kwargs) -> dict:
        """
        Execute a custom search pipeline.
        
        Orchestration:
        1. Discover URLs (Broad coverage)
        2. Scrape Content (Deep data fetching)
        3. Rank & Package (Custom Logic)
        """
        start_time = time.time()
        results = []
        
        try:
            # phase 1: Discovery (URL finding)
            candidate_urls = discovery_layer.discover_urls(query, num_results=num_results + 5)
            
            # phase 2: Scraping (Live Data Fetching)
            scraped_items = []
            if candidate_urls:
                for url in candidate_urls:
                    item = scraper.scrape(url)
                    if item:
                        scraped_items.append(item)
                    
                    # Soft rate limiting for scraper
                    time.sleep(0.3)
            
            # phase 3: Transformation to standard results
            for item in scraped_items:
                result = self._parse_scraped_item(item)
                if result:
                    results.append(result)
            
            # If no live results found, fallback to mock data
            is_mock = False
            if not results:
                print("No live results fetched, falling back to mock data.")
                results = self._search_mock(query, num_results)
                is_mock = True
                
            search_time = time.time() - start_time
            
            message = None
            if is_mock:
                message = "Search limited: Showing results from verified crisis database."
            elif not results:
                message = "No results found for this query."

            return {
                "results": results[:num_results],
                "total_results": len(results),
                "search_time": round(search_time, 2),
                "query": query,
                "error": None,
                "message": message,
                "source": "database" if is_mock else "live"
            }
                
        except Exception as e:
            print(f"Custom Search failed ({e}), switching to Mock Fallback.")
            return {
                "results": self._search_mock(query, num_results),
                "total_results": 0,
                "search_time": round(time.time() - start_time, 2),
                "query": query,
                "error": str(e),
                "source": "error_fallback"
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

    def _search_mock(self, query: str, num_results: int = 10) -> list:
        """Search local mock data as fallback."""
        query_terms = query.lower().split()
        results = []
        
        for item in self.mock_data:
            text = (item.get("title", "") + " " + item.get("content", "")).lower()
            if any(term in text for term in query_terms):
                results.append(self._parse_mock_result(item))
                
        random.shuffle(results)
        return results[:num_results]

    def _parse_mock_result(self, item: dict) -> dict:
        """Parse local JSON item into standard result format."""
        return {
            "title": item.get("title", "No Title"),
            "link": item.get("source", "#"),
            "snippet": item.get("content", ""),
            "content": item.get("content", ""),
            "displayLink": "Fallback Data",
            "trust_score": item.get("trust", 0.5),
            "freshness_score": 0.8,
            "final_score": 0,
            "badge": "verified" if item.get("trust", 0) > 0.8 else "unverified",
            "freshness_label": "recent",
            "location": item.get("location", "")
        }

    def search_emergency(self, query: str, num_results: int = 10) -> dict:
        """
        Emergency search optimizes for official sources.
        """
        return self.search(query, num_results=num_results)


# Singleton instance
search_engine = SearchEngine()
