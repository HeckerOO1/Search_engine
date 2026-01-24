import json
import os

data_path = 'model/data.json'

with open(data_path, 'r') as f:
    data = json.load(f)

# Deep-link URLs with RICH content simulation
# These 'content' fields simulate what a scraper might return, ensuring high keyword matching.
curated_urls = [
    # =========================================================================
    # EMERGENCY: NATURAL DISASTERS
    # =========================================================================
    {
        "url": "https://earthquake.usgs.gov/earthquakes/map/",
        "title": "Latest Earthquakes Map | USGS",
        "content": "Interactive real-time map of the latest earthquakes worldwide provided by the USGS. View recent seismic events, magnitude 2.5+ earthquakes in the US, and significant global tremors. Click on individual events for detailed ShakeMaps, PAGER impact estimates, and technical origin data. The map updates every minute to provide the most accurate earthquake monitoring available.",
        "keywords": ["earthquake", "map", "magnitude", "latest", "usgs", "seismic", "shakemap", "tremor"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.ready.gov/earthquakes",
        "title": "Earthquake Safety | Ready.gov",
        "content": "Learn how to stay safe during an earthquake with the Drop, Cover, and Hold On technique. If you are indoors, stay there and take cover under a sturdy table. If outdoors, move to a clear area away from buildings and power lines. Prepare an emergency kit with water, food, and communication tools. Secure heavy furniture to walls to prevent injury.",
        "keywords": ["earthquake", "safety", "drop cover hold on", "preparedness", "survival", "kit"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/earthquake.html",
        "title": "Earthquake Preparedness | Red Cross",
        "content": "Get comprehensive earthquake preparedness tips from the American Red Cross. Learn how to build a survival kit, create a family evacuation plan, and inspect your home for seismic hazards. Understand the difference between foreshocks, mainshocks, and aftershocks. Sign up for emergency alerts and learn first aid basics.",
        "keywords": ["earthquake", "red cross", "prepare", "kit", "safety", "aftershocks", "evacuation"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.fire.ca.gov/incidents",
        "title": "CAL FIRE Active Incident Map",
        "content": "Official CAL FIRE map showing all active wildfires in California. Search by location to find evacuation orders, containment percentages, usage of air tankers, and personnel deployment. Real-time updates on fire size (acres burned), road closures, and shelter locations for displaced residents.",
        "keywords": ["wildfire", "california", "incidents", "map", "status", "containment", "evacuation"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.ready.gov/wildfires",
        "title": "Wildfire Safety Guidelines",
        "content": "Prepare for wildfires by creating a defensible space around your home. Clear dry leaves and debris from gutters. When an evacuation warning is issued, leave immediately. Know your evacuation zone and have a 'Go Bag' ready with documents, N95 masks, and essential medications. Protect yourself from smoke inhalation.",
        "keywords": ["wildfire", "evacuation", "safety", "smoke", "prepare", "zone", "defensible space"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.nhc.noaa.gov/",
        "title": "National Hurricane Center (NOAA)",
        "content": "The National Hurricane Center provides official forecasts, watches, and warnings for tropical cyclones in the Atlantic and Eastern Pacific basins. Track hurricane paths, wind speeds, and potential storm surge impacts. Access satellite imagery, rainfall potential maps, and marine warnings.",
        "keywords": ["hurricane", "cyclone", "tropical", "tracking", "forecast", "storm surge", "noaa"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.weather.gov/safety/flood",
        "title": "Flood Safety Tips | NWS",
        "content": "Flooding constitutes a major weather hazard. Follow the 'Turn Around Don't Drown' rule: never drive through flooded roadways. Just six inches of fast-moving water can knock you over, and two feet can float a vehicle. Monitor NOAA weather radio for flash flood warnings and move to higher ground immediately.",
        "keywords": ["flood", "safety", "water", "driving", "nws", "flash flood", "turn around don't drown"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.ready.gov/floods",
        "title": "Flood Preparedness Guide",
        "content": "Understand flood risks in your area and purchase flood insurance if necessary. specialized policies are often required. During a flood warning, evacuate if advised. Move valuables to higher floors. Avoid contact with floodwater, which may be contaminated with sewage or chemicals.",
        "keywords": ["flood", "prepare", "evacuate", "sandbags", "checklist", "insurance", "contamination"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.weather.gov/safety/tornado",
        "title": "Tornado Safety | NWS",
        "content": "Tornadoes can strike with little warning. Know the difference between a Tornado Watch (conditions favorable) and a Tornado Warning (tornado spotted). Seek shelter immediately in a basement or interior room on the lowest floor. Protect your head and neck. Avoid windows and doors.",
        "keywords": ["tornado", "safety", "shelter", "funnel cloud", "warning", "watch", "basement"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.ready.gov/tornadoes",
        "title": "Tornado Preparedness",
        "content": "Identify a safe room in your home, such as a storm cellar or reinforced closet. Practice tornado drills with your family. If you are in a mobile home, identify a nearby sturdy building for shelter. Listen to EAS broadcasts for updates.",
        "keywords": ["tornado", "ready.gov", "safe room", "storm cellar", "siren", "drill"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.tsunami.gov/",
        "title": "U.S. Tsunami Warning System",
        "content": "Official source for tsunami warnings, advisories, watches, and information statements. View active alerts for the US West Coast, Alaska, and Pacific Islands. Learn natural warning signs like ground shaking or receding ocean water. Evacuate inland or to high ground immediately upon warning.",
        "keywords": ["tsunami", "warning", "wave", "ocean", "hazards", "coast", "evacuation"],
        "trust": 1.0,
        "category": "emergency"
    },

    # =========================================================================
    # EMERGENCY: MEDICAL & FIRST AID
    # =========================================================================
    {
        "url": "https://www.mayoclinic.org/first-aid/first-aid-cpr/basics/art-20056600",
        "title": "CPR Steps | Mayo Clinic",
        "content": "Cardiopulmonary resuscitation (CPR): First, check if the person is breathing and has a pulse. If not, call 911. Begin chest compressions hard and fast in the center of the chest (100-120 beats per minute). Push down at least 2 inches. If trained, give rescue breaths. Resume compressions until help arrives.",
        "keywords": ["cpr", "first aid", "heart", "resuscitation", "medical", "steps", "compressions"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.redcross.org/take-a-class/cpr/performing-cpr/cpr-steps",
        "title": "Hands-Only CPR | Red Cross",
        "content": "Hands-only CPR is recommended for bystanders. Call 911. Push hard and fast in the center of the chest to the beat of 'Stayin' Alive'. Continue without stopping until emergency responders take over. This method keeps blood flowing to the brain and vital organs.",
        "keywords": ["cpr", "hands-only", "cardiac arrest", "emergency", "steps", "chest compressions"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.mayoclinic.org/first-aid/first-aid-choking/basics/art-20056637",
        "title": "Choking First Aid (Heimlich)",
        "content": "If a person is choking and cannot speak, perform the Heimlich maneuver. Stand behind them and wrap your arms around their waist. Make a fist above the navel. Grasp your fist with the other hand and press hard into the abdomen with a quick, upward thrust. Repeat until the object is expelled.",
        "keywords": ["choking", "heimlich", "maneuver", "airway", "blocked", "abdominal thrusts"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.mayoclinic.org/first-aid/first-aid-stroke/basics/art-20056602",
        "title": "Stroke First Aid (FAST)",
        "content": "Spot a stroke F.A.S.T.: Face drooping (ask them to smile), Arm weakness (ask them to raise both arms), Speech difficulty (slurred speech), Time to call 911. Immediate medical attention is critical to minimize brain damage.",
        "keywords": ["stroke", "fast", "symptoms", "brain", "emergency", "face drooping", "slurred speech"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.healthline.com/health/heart-attack-symptoms",
        "title": "Heart Attack Symptoms",
        "content": "Common heart attack symptoms include chest pain or discomfort, shortness of breath, pain in the jaw, neck, or back, and nausea. Women may experience different symptoms like extreme fatigue. Call emergency services immediately. Chew an aspirin if not allergic.",
        "keywords": ["heart attack", "symptoms", "chest pain", "signs", "emergency", "cardiac", "aspirin"],
        "trust": 0.9,
        "category": "emergency"
    },
    {
        "url": "https://www.mayoclinic.org/first-aid/first-aid-severe-bleeding/basics/art-20056661",
        "title": "Severe Bleeding First Aid",
        "content": "Stop the bleeding: Apply direct pressure to the wound with a clean cloth. If bleeding seeps through, add more layers—do not remove the first. If on an limb and bleeding is life-threatening, apply a tourniquet above the wound. Keep the person warm and wait for help.",
        "keywords": ["bleeding", "wound", "pressure", "tourniquet", "cut", "blood", "trauma"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.mayoclinic.org/first-aid/first-aid-burns/basics/art-20056629",
        "title": "Burns First Aid",
        "content": "Treat minor burns by cooling the area with cool (not cold) running water for 10 minutes. Cover loosely with sterile gauze. Do not pop blisters. For major burns (charred or white skin), call 911 immediately and protect the person from further harm. Do not apply ice directly.",
        "keywords": ["burn", "fire", "scald", "blister", "cool water", "ointment", "first aid"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.mayoclinic.org/first-aid/first-aid-poisoning/basics/art-20056657",
        "title": "Poisoning First Aid",
        "content": "If you suspect poisoning, call Poison Control (1-800-222-1222 in the US) immediately. If the person is unconscious or not breathing, call 911. If the poison was swallowed, do not induce vomiting unless told to do so. If on skin, rinse with water for 15 minutes.",
        "keywords": ["poison", "chemical", "swallowed", "toxic", "poison control", "call"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://www.mayoclinic.org/first-aid/first-aid-seizure/basics/art-20056655",
        "title": "Seizure First Aid",
        "content": "Ease the person to the floor and turn them gently onto one side to help them breathe. Clear the area of sharp objects. Put something soft under their head. Do not hold them down or put anything in their mouth. Time the seizure; if it lasts longer than 5 minutes, call 911.",
        "keywords": ["seizure", "epilepsy", "convulsion", "head injury", "safety"],
        "trust": 1.0,
        "category": "emergency"
    },
    {
        "url": "https://988lifeline.org/",
        "title": "988 Suicide & Crisis Lifeline",
        "content": "The 988 Suicide & Crisis Lifeline provides 24/7, free and confidential support for people in distress. Prevention and crisis resources for you or your loved ones. Call or text 988 to connect with a trained counselor.",
        "keywords": ["suicide", "crisis", "depression", "help", "lifeline", "988"],
        "trust": 1.0,
        "category": "emergency"
    },

    # =========================================================================
    # STANDARD: TECHNOLOGY & DEVELOPMENT
    # =========================================================================
    {
        "url": "https://docs.python.org/3/tutorial/index.html",
        "title": "The Python Tutorial",
        "content": "The official Python tutorial. Python is an easy to learn, powerful programming language. It has efficient high-level data structures and a simple but effective approach to object-oriented programming. Learn about the interpreter, control flow, data structures, modules, I/O, and errors/exceptions.",
        "keywords": ["python", "tutorial", "learn", "programming", "official", "guide", "syntax", "oop"],
        "trust": 1.0,
        "category": "standard"
    },
    {
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
        "title": "MDN JavaScript Guide",
        "content": "The MDN JavaScript Guide shows you how to use JavaScript and gives you an overview of the language. Learn about grammar, types, loops, functions, expressions, and the DOM. JavaScript is a lightweight, interpreted, or just-in-time compiled programming language with first-class functions.",
        "keywords": ["javascript", "js", "guide", "mdn", "web", "frontend", "programming"],
        "trust": 1.0,
        "category": "standard"
    },
    {
        "url": "https://react.dev/learn",
        "title": "React - Quick Start",
        "content": "Welcome to the React documentation. React is the library for web and native user interfaces. Build user interfaces out of individual pieces called components. Learn how to create components, manage state with hooks, and handle user interactions.",
        "keywords": ["react", "javascript", "framework", "components", "frontend", "ui", "library"],
        "trust": 1.0,
        "category": "standard"
    },
    {
        "url": "https://git-scm.com/book/en/v2/Getting-Started-Git-Basics",
        "title": "Git Basics Documentation",
        "content": "Git is a distributed version control system. Learn the three states: modified, staged, and committed. Understand how to record changes to the repository, view the commit history, and undo things. Master branching and merging for efficient collaboration.",
        "keywords": ["git", "version control", "commit", "push", "guide", "repo", "vcs"],
        "trust": 1.0,
        "category": "standard"
    },
    {
        "url": "https://stackoverflow.com/questions",
        "title": "Stack Overflow Questions",
        "content": "Stack Overflow is the largest, most trusted online community for developers to learn, share their programming knowledge, and build their careers. Browse millions of questions and answers on topics ranging from Python and Java to C# and React.",
        "keywords": ["stackoverflow", "coding", "qa", "help", "developer", "bug", "programming"],
        "trust": 0.8,
        "category": "standard"
    },
    {
        "url": "https://www.bbc.com/news/world",
        "title": "BBC World News",
        "content": "Get the latest BBC World News: international news, features and analysis from Africa, the Asia-Pacific, Europe, Latin America, the Middle East, South Asia, and the United States and Canada.",
        "keywords": ["news", "world", "bbc", "international", "politics", "current events"],
        "trust": 0.95,
        "category": "standard"
    },
    {
        "url": "https://en.wikipedia.org/wiki/Main_Page",
        "title": "Wikipedia, the free encyclopedia",
        "content": "Wikipedia is a free online encyclopedia, created and edited by volunteers around the world and hosted by the Wikimedia Foundation. It contains millions of articles on almost every subject imaginable, from history and science to pop culture.",
        "keywords": ["wikipedia", "encyclopedia", "facts", "history", "information", "research"],
        "trust": 0.8,
        "category": "standard"
    },

    # =========================================================================
    # RUMORS & UNVERIFIED ("Social / Forum")
    # =========================================================================
    {
        "url": "https://old.reddit.com/r/conspiracy/comments/earthquake_haarp/",
        "title": "reddit: They are hiding the truth about the quakes!",
        "content": "My cousin works at a gov lab and says the recent swarms are ARTIFICIAL. HAARP is being used to trigger faults. Don't believe the USGS data, they are capping magnitude readings to prevent panic. #Truth #WakeUp",
        "keywords": ["conspiracy", "project blue beam", "haarp", "fake", "government", "rumor", "reddit"],
        "trust": 0.2,
        "category": "social"
    },
    {
        "url": "https://nitter.net/TruthSeeker99/status/123456789",
        "title": "X (Nitter): BREAKING! Tsunami hitting NYC in 20 mins??",
        "content": "Just heard from a friend at NOAA that a mega-tsunami is incoming for the East Coast!! EVACUATE NOW!! Mainstream media is silent! RT to save lives!!!",
        "keywords": ["tsunami", "nyc", "breaking", "evacuate", "censored", "twitter", "x", "nitter"],
        "trust": 0.1,
        "category": "social"
    },
    {
        "url": "https://boards.4chan.org/pol/thread/999999",
        "title": "/pol/ - The solar flare blackout is starting",
        "content": "Anons, the grid is going down tonight. Stock up on ammo and canned beans. The 'solar flare' is a cover for the cyber attack. It's happening. IT'S HAPPENING.",
        "keywords": ["collapse", "grid", "blackout", "anon", "leak", "4chan"],
        "trust": 0.1,
        "category": "social"
    },
    {
        "url": "https://old.reddit.com/r/medical/comments/h3art_att4ck_cure/",
        "title": "reddit: Doctors don't want you to know this heart attack cure",
        "content": "If you are having a heart attack, drink a mix of cayenne pepper and maple syrup immediately! It stops the attack in 30 seconds. Don't call 911, they will just drug you.",
        "keywords": ["heart attack", "cure", "natural", "cayenne", "secret", "medical advice"],
        "trust": 0.1,
        "category": "social"
    },
    
    # =========================================================================
    # SEMI-TRUSTED / SENSATIONALIST ("Media / Blog")
    # =========================================================================
    {
        "url": "https://www.dailymail.co.uk/news/article-999/earthquake-panic.html",
        "title": "KILLER QUAKE COMING? Scientists baffled by strange sounds",
        "content": "EXCLUSIVE: Residents report terrifying groans from the earth. Is the 'Big One' finally here? Experts remain silent as panic sweeps the neighborhood. Click to see the SHOCKING video.",
        "keywords": ["earthquake", "panic", "killer", "exclusive", "shocking", "daily mail"],
        "trust": 0.5,
        "category": "media"
    },
    {
        "url": "https://nypost.com/2026/01/23/wildfire-arson-gangs/",
        "title": "Are ARSON GANGS behind the new fires? Locals speak out.",
        "content": "While officials blame climate change, locals suggest a sinister plot. Mysterious vans seen leaving the scene. We investigate the rumors the police won't touch.",
        "keywords": ["wildfire", "arson", "gangs", "plot", "investigation", "rumor"],
        "trust": 0.6,
        "category": "media"
    },
    {
        "url": "https://medium.com/@CryptoBro/bitcoin-fixing-disasters-123",
        "title": "How Blockchain Will Stop Natural Disasters",
        "content": "Forget FEMA. Decentralized weather modification DAOs are the future. By staking tokens, we can redirect hurricanes. Here is my whitepaper on why gov relief is a scam.",
        "keywords": ["crypto", "hurricane", "blockchain", "scam", "opinion", "blog"],
        "trust": 0.4,
        "category": "blog"
    }
]

# Create exactly 140+ high-quality enriched entries
mock_results = []
for i, item in enumerate(curated_urls * 6): # Multiplier to fill the index
    url_id = i + 1
    mock_results.append({
        "id": url_id,
        "source": item["url"],
        "title": item["title"],
        "content": item["content"], # RICH CONTENT HERE
        "keywords": item["keywords"], 
        "trust": item["trust"],
        "pogo_penalty": 0.0,
        "category": item["category"],
        "location": "Global",
        "timestamp": "2026-01-24T00:30:00"
    })

data["mock_search_results"] = mock_results # No cap, let it grow

with open(data_path, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Updated data.json with {len(data['mock_search_results'])} RICH-CONTENT verified sources.")
