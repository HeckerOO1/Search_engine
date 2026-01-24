# tracks what users do - like when they click results and come back quick
# helps us figure out which results suck (pogo-sticking = bad result)

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import POGO_STICK_THRESHOLD_SECONDS, POGO_STICK_PENALTY


class BehaviorTracker:
    # keeps track of user behavior to make search results better
    
    def __init__(self):
        self.click_events: Dict[str, List[datetime]] = {}  # when people clicked stuff
        
        self.pogo_counts: Dict[str, int] = {}  # how many times people bounced back from each URL
        
        self.last_click: Optional[dict] = None  # remember the last thing they clicked
        
        self.penalties: Dict[str, float] = {}  # penalty scores for bad results
        
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.json')  # where we save stuff
        
        # load any saved penalties from last time
        self._load_from_storage()
    
    def record_click(self, url: str, query: str) -> dict:
        # save when someone clicks a result
        now = datetime.now()
        
        if url not in self.click_events:
            self.click_events[url] = []
        
        self.click_events[url].append(now)
        
        # remember this click so we can detect if they come back quick
        self.last_click = {
            "url": url,
            "query": query,
            "timestamp": now
        }
        
        if url not in self.penalties:
            # first time seeing this URL, lets start tracking it
            print(f"[Tracker] New URL detected: {url}. Registering...")
            self.penalties[url] = 0.0
            self._create_dynamic_entry(url, query)

        return {
            "recorded": True,
            "url": url,
            "timestamp": now.isoformat()
        }
    
    def record_return(self, from_url: str) -> dict:
        # someone came back from a result - lets see if they bounced quick (pogo-stick)
        now = datetime.now()
        
        if not self.last_click or self.last_click["url"] != from_url:
            return {"pogo_detected": False, "reason": "no matching click"}
        
        # how long were they gone for?
        time_spent = (now - self.last_click["timestamp"]).total_seconds()
        
        if time_spent < POGO_STICK_THRESHOLD_SECONDS:
            # yep they bounced back quick, thats a pogo!
            if from_url not in self.pogo_counts:
                self.pogo_counts[from_url] = 0
            
            self.pogo_counts[from_url] += 1
            
            # add penalty to this result
            current_penalty = self.penalties.get(from_url, 0.0)
            self.penalties[from_url] = min(1.0, current_penalty + POGO_STICK_PENALTY)
            
            # save it to file
            self._sync_to_storage(from_url, self.penalties[from_url])
            
            return {
                "pogo_detected": True,
                "time_spent_seconds": round(time_spent, 1),
                "pogo_count": self.pogo_counts[from_url],
                "penalty": self.penalties[from_url],
                "penalty_applied": True
            }
        else:
            # they stayed long enough, thats good! reduce penalty a bit
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
        # how much penalty does this URL have?
        return self.penalties.get(url, 0.0)
    
    def get_pogo_count(self, url: str) -> int:
        # how many pogos for this URL?
        return self.pogo_counts.get(url, 0)
    
    def get_stats(self) -> dict:
        # just some overall stats
        return {
            "total_urls_tracked": len(self.click_events),
            "urls_with_pogo": len(self.pogo_counts),
            "urls_penalized": len(self.penalties),
            "total_pogo_events": sum(self.pogo_counts.values())
        }
    
    def cleanup_old_data(self, hours: int = 24):
        # delete old click data to save memory
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for url in list(self.click_events.keys()):
            self.click_events[url] = [
                ts for ts in self.click_events[url] if ts > cutoff
            ]
            if not self.click_events[url]:
                del self.click_events[url]
    
    def _load_from_storage(self):
        # load saved penalties from data.json
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
        # save penalty to data.json
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
                # not in file yet, create new entry
                self._create_dynamic_entry(url, "discovered")
                
        except Exception as e:
            print(f"Error syncing behavior data: {e}")

    def calculate_trust(self, url: str) -> float:
        # figure out how trustworthy a domain is based on its URL
        # .gov and .edu = super trusted
        # wikipedia, github etc = very trusted
        # random sites = not so much
        lower_url = url.lower()
        
        # government and education sites
        if ".gov" in lower_url or ".edu" in lower_url:
            return 0.85
            
        # well known trusted sites
        high_trust_domains = [
            "wikipedia.org", "github.com", "bbc.com", "cnn.com", 
            "nytimes.com", "reuters.com", "who.int", "nasa.gov",
            "stackoverflow.com", "medium.com"
        ]
        
        for domain in high_trust_domains:
            if domain in lower_url:
                return 0.9
        
        # kinda trusted (reddit, youtube etc)
        semi_trusted_domains = [
            "reddit.com", "quora.com", "youtube.com", "linkedin.com"
        ]
        
        for domain in semi_trusted_domains:
            if domain in lower_url:
                return 0.6
                
        # dont know this site, give it low trust
        return 0.4

    def _create_dynamic_entry(self, url: str, query: str):
        # add a new URL to data.json when we see it for first time
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
            
            # make sure it doesnt already exist
            for item in data.get("mock_search_results", []):
                if item["source"] == url:
                    return

            new_id = len(data.get("mock_search_results", [])) + 1
            
            # figure out how much to trust this domain
            trust_score = self.calculate_trust(url)
            
            new_entry = {
                "id": new_id,
                "source": url,
                "title": f"Dynamic Result: {query}",
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


# make one instance and use it everywhere
behavior_tracker = BehaviorTracker()
