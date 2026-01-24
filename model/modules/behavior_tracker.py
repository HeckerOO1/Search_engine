"""User Behavior Tracking Module.

Tracks user interactions like pogo-sticking (quick returns)
to identify low-quality or misleading results.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import POGO_STICK_THRESHOLD_SECONDS, POGO_STICK_PENALTY


class BehaviorTracker:
    """Tracks user behavior to improve result ranking."""
    
    def __init__(self):
        # Store click events: {result_url: [click_timestamps]}
        self.click_events: Dict[str, List[datetime]] = {}
        
        # Store pogo-stick counts: {result_url: count}
        self.pogo_counts: Dict[str, int] = {}
        
        # Store last click for pogo detection
        self.last_click: Optional[dict] = None
        
        # Session penalties: {result_url: penalty_score}
        self.penalties: Dict[str, float] = {}
        
        # Path to data.json
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.json')
        
        # Load existing penalties from data.json
        self._load_from_storage()
    
    def record_click(self, url: str, query: str) -> dict:
        """
        Record when a user clicks on a search result.
        
        Args:
            url: The URL that was clicked
            query: The search query associated with the click
            
        Returns:
            dict with click metadata
        """
        now = datetime.now()
        
        if url not in self.click_events:
            self.click_events[url] = []
        
        self.click_events[url].append(now)
        
        # Store for pogo detection
        self.last_click = {
            "url": url,
            "query": query,
            "timestamp": now
        }
        
        if url not in self.penalties:
            # New URL encountered! Register it for tracking.
            print(f"[Tracker] New URL detected: {url}. Registering...")
            self.penalties[url] = 0.0
            self._create_dynamic_entry(url, query)

        return {
            "recorded": True,
            "url": url,
            "timestamp": now.isoformat()
        }
    
    def record_return(self, from_url: str) -> dict:
        """
        Record when a user returns from a clicked result.
        Detects pogo-sticking behavior.
        
        Args:
            from_url: The URL the user returned from
            
        Returns:
            dict with pogo-stick detection results
        """
        now = datetime.now()
        
        if not self.last_click or self.last_click["url"] != from_url:
            return {"pogo_detected": False, "reason": "no matching click"}
        
        # Calculate time spent on page
        time_spent = (now - self.last_click["timestamp"]).total_seconds()
        
        if time_spent < POGO_STICK_THRESHOLD_SECONDS:
            # Pogo-sticking detected!
            if from_url not in self.pogo_counts:
                self.pogo_counts[from_url] = 0
            
            self.pogo_counts[from_url] += 1
            
            # Update penalty
            current_penalty = self.penalties.get(from_url, 0.0)
            self.penalties[from_url] = min(1.0, current_penalty + POGO_STICK_PENALTY)
            
            # Sync to data.json
            self._sync_to_storage(from_url, self.penalties[from_url])
            
            return {
                "pogo_detected": True,
                "time_spent_seconds": round(time_spent, 1),
                "pogo_count": self.pogo_counts[from_url],
                "penalty": self.penalties[from_url],
                "penalty_applied": True
            }
        else:
            # Reward for staying: decrease penalty
            if from_url in self.penalties and self.penalties[from_url] > 0:
                self.penalties[from_url] = max(0.0, self.penalties[from_url] - 0.1)
                self._sync_to_storage(from_url, self.penalties[from_url])
                
            return {
                "pogo_detected": False,
                "time_spent_seconds": round(time_spent, 1),
                "reason": "sufficient time spent on page",
                "penalty_reduced": from_url in self.penalties
            }
    
    def get_penalty(self, url: str) -> float:
        """
        Get the ranking penalty for a URL based on user behavior.
        
        Args:
            url: The URL to check
            
        Returns:
            float penalty score (0 = no penalty, higher = worse)
        """
        return self.penalties.get(url, 0.0)
    
    def get_pogo_count(self, url: str) -> int:
        """Get the pogo-stick count for a URL."""
        return self.pogo_counts.get(url, 0)
    
    def get_stats(self) -> dict:
        """Get overall behavior tracking statistics."""
        return {
            "total_urls_tracked": len(self.click_events),
            "urls_with_pogo": len(self.pogo_counts),
            "urls_penalized": len(self.penalties),
            "total_pogo_events": sum(self.pogo_counts.values())
        }
    
    def cleanup_old_data(self, hours: int = 24):
        """Clean up data older than specified hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for url in list(self.click_events.keys()):
            self.click_events[url] = [
                ts for ts in self.click_events[url] if ts > cutoff
            ]
            if not self.click_events[url]:
                del self.click_events[url]
    
    def _load_from_storage(self):
        """Load penalties from data.json"""
        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r') as f:
                    data = json.load(f)
                    for item in data.get("mock_search_results", []):
                        if "pogo_penalty" in item:
                            self.penalties[item["source"]] = item["pogo_penalty"]
        except Exception as e:
            print(f"Error loading behavior data: {e}")

    def _sync_to_storage(self, url: str, penalty: float):
        """Update a specific URL's penalty in data.json"""
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
            
            updated = False
            for item in data.get("mock_search_results", []):
                if item["source"] == url:
                    item["pogo_penalty"] = round(penalty, 3)
                    updated = True
                    break
            
            if updated:
                with open(self.data_path, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                # If we tried to sync but it wasn't there, create it now (fallback)
                self._create_dynamic_entry(url, "discovered")
                
        except Exception as e:
            print(f"Error syncing behavior data: {e}")

    def calculate_trust(self, url: str) -> float:
        """
        Calculate trust score based on domain authority.
        
        Rules:
        - .gov, .edu -> 0.85 (High Trust)
        - Known Authorities (wiki, github, etc.) -> 0.9 (Very High Trust)
        - Semi-trusted -> 0.5 - 0.8
        - Unknown/Generic -> 0.4 (Low Trust)
        """
        lower_url = url.lower()
        
        # 1. High Trust TLDs
        if ".gov" in lower_url or ".edu" in lower_url:
            return 0.85
            
        # 2. Known Authorities Whitelist
        high_trust_domains = [
            "wikipedia.org", "github.com", "bbc.com", "cnn.com", 
            "nytimes.com", "reuters.com", "who.int", "nasa.gov",
            "stackoverflow.com", "medium.com"
        ]
        
        for domain in high_trust_domains:
            if domain in lower_url:
                return 0.9
        
        # 3. Semi-Trusted (Common aggregators)
        semi_trusted_domains = [
            "reddit.com", "quora.com", "youtube.com", "linkedin.com"
        ]
        
        for domain in semi_trusted_domains:
            if domain in lower_url:
                return 0.6
                
        # 4. Default / Unknown
        return 0.4

    def _create_dynamic_entry(self, url: str, query: str):
        """Create a new entry in data.json for a dynamically discovered URL."""
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
            
            # double check it doesn't exist
            for item in data.get("mock_search_results", []):
                if item["source"] == url:
                    return

            new_id = len(data.get("mock_search_results", [])) + 1
            
            # Calculate dynamic trust
            trust_score = self.calculate_trust(url)
            
            new_entry = {
                "id": new_id,
                "source": url,
                "title": f"Dynamic Result: {query}", # Placeholder title
                "content": f"Dynamically visited page for query: {query}",
                "keywords": query.split(),
                "trust": trust_score, 
                "pogo_penalty": 0.0,
                "category": "dynamic",
                "location": "Global",
                "timestamp": datetime.now().isoformat()
            }
            
            data["mock_search_results"].append(new_entry)
            
            with open(self.data_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"[Tracker] Registered new dynamic URL: {url} | Trust: {trust_score}")
            
        except Exception as e:
            print(f"Error creating dynamic entry: {e}")


# Global tracker instance
behavior_tracker = BehaviorTracker()
