"""DuckDuckGo Search Module.

Uses duckduckgo-search library for reliable search results.
No API key required!
"""

from duckduckgo_search import DDGS
from typing import List, Dict
import time


class SearchEngine:
    """DuckDuckGo search engine using official library."""
    
    def __init__(self):
        pass
    
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
            return {
                "error": f"Search failed: {str(e)}",
                "results": [],
                "total_results": 0,
                "query": query
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
