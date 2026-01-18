import re
from datetime import datetime

class EmergencyDetector:
    def __init__(self):
        self.emergency_keywords = [
            "earthquake", "flood", "tsunami", "cyclone", "hurricane", 
            "fire", "wildfire", "landslide", "explosion", "terror", 
            "attack", "bomb", "collapse", "urgent", "help", "sos", 
            "evacuate", "casualty", "death", "injured", "save", "victim"
        ]
        
        self.pattern = re.compile(r'\b(' + '|'.join(self.emergency_keywords) + r')\b', re.IGNORECASE)

    def is_emergency(self, query):
        
        if not query:
            return False, 0.0
        
        matches = self.pattern.findall(query)
        if matches:
        
            confidence = min(1.0, 0.6 + (len(matches) * 0.1))
            return True, confidence
        
        return False, 0.0
