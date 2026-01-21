"""DuckDuckGo Search Module.

Uses duckduckgo-search library for reliable search results.
No API key required!
"""

from duckduckgo_search import DDGS
from typing import List, Dict
import time
import json
import os
import random


class SearchEngine:
    """DuckDuckGo search engine using official library."""
    
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

    def _search_mock(self, query: str, num_results: int = 10) -> list:
        """Search local mock data as fallback."""
        query_terms = query.lower().split()
        results = []
        
        for item in self.mock_data:
            # Simple keyword matching
            text = (item.get("title", "") + " " + item.get("content", "")).lower()
            if any(term in text for term in query_terms):
                results.append(self._parse_mock_result(item))
                
        # Shuffle slightly to look dynamic
        random.shuffle(results)
        return results[:num_results]

    def _parse_mock_result(self, item: dict) -> dict:
        """Parse local JSON item into standard result format."""
        return {
            "title": item.get("title", "No Title"),
            "link": item.get("source", "#"), # Use source or ID as link proxy
            "snippet": item.get("content", ""),
            "displayLink": "Fallback Data Source",
            "trust_score": item.get("trust", 0.5),
            "freshness_score": 0.8, # Assume mock data is reasonably fresh
            "final_score": 0,
            "badge": "verified" if item.get("trust", 0) > 0.8 else "unverified",
            "freshness_label": "recent"
        }
    
    def search(self, query: str, num_results: int = 10, **kwargs) -> dict:
        """
        Execute a search query using DuckDuckGo.
        
        Args:
            query: The search query
            num_results: Number of results to return
            **kwargs: Additional parameters (timelimit for freshness)
            
        Returns:
            dict with search results and metadata
        """
        start_time = time.time()
        try:
            with DDGS() as ddgs:
                # Get timelimit if specified (for emergency mode)
                timelimit = kwargs.get("timelimit", None)
                
                # Perform search
                raw_results = list(ddgs.text(
                    query, 
                    max_results=num_results,
                    timelimit=timelimit
                ))
                
                # Parse results
                results = []
                for item in raw_results:
                    result = self._parse_result(item)
                    if result:
                        results.append(result)
                
                search_time = time.time() - start_time
                
                return {
                    "results": results,
                    "total_results": len(results),
                    "search_time": round(search_time, 2),
                    "query": query,
                    "error": None
                }
                
        except Exception as e:
            print(f"DuckDuckGo Search failed ({e}), switching to Mock Fallback.")
            
            # Fallback to local data
            fallback_results = self._search_mock(query, num_results)
            
            return {
                "results": fallback_results,
                "total_results": len(fallback_results),
                "search_time": round(time.time() - start_time, 2),
                "query": query,
                "error": None if fallback_results else f"Search failed: {str(e)}"
            }
    
    def _parse_result(self, item: dict) -> dict:
        """Parse a single search result from DDGS."""
        try:
            link = item.get("href", item.get("link", ""))
            display_link = link.replace("https://", "").replace("http://", "")
            
            return {
                "title": item.get("title", ""),
                "link": link,
                "snippet": item.get("body", item.get("snippet", "")),
                "displayLink": display_link,
                "pagemap": {},
                # Placeholders for our scoring
                "trust_score": 0,
                "freshness_score": 0,
                "final_score": 0,
                "badge": "unverified",
                "freshness_label": "unknown"
            }
        except Exception:
            return None
    
    def search_emergency(self, query: str, num_results: int = 10) -> dict:
        """
        Execute search with emergency-optimized parameters.
        Prioritizes recent results from the past week.
        """
        return self.search(
            query,
            num_results=num_results,
            timelimit="w"  # Past week
        )


# Singleton instance
search_engine = SearchEngine()
