"""User Behavior Tracking Module.

Tracks user interactions like pogo-sticking (quick returns)
to identify low-quality or misleading results.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import POGO_STICK_THRESHOLD_SECONDS, POGO_STICK_PENALTY, MAX_POGO_COUNT_BEFORE_DEMOTE


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
            
            # Update penalty if threshold exceeded
            if self.pogo_counts[from_url] >= MAX_POGO_COUNT_BEFORE_DEMOTE:
                self.penalties[from_url] = POGO_STICK_PENALTY
            
            return {
                "pogo_detected": True,
                "time_spent_seconds": round(time_spent, 1),
                "pogo_count": self.pogo_counts[from_url],
                "threshold": MAX_POGO_COUNT_BEFORE_DEMOTE,
                "penalty_applied": self.pogo_counts[from_url] >= MAX_POGO_COUNT_BEFORE_DEMOTE
            }
        else:
            return {
                "pogo_detected": False,
                "time_spent_seconds": round(time_spent, 1),
                "reason": "sufficient time spent on page"
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
                # Also clean up related data
                self.pogo_counts.pop(url, None)
                self.penalties.pop(url, None)


# Global tracker instance
behavior_tracker = BehaviorTracker()
