import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import time

class Scraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape(self, url: str) -> Optional[Dict]:
        """Fetch and parse content from a URL."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Clean up the soup
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Extract basic info
            title = soup.title.string if soup.title else "No Title"
            
            # Smart content extraction (heuristic-based)
            # We look for the longest paragraph blocks or specific article tags
            article = soup.find('article')
            if article:
                text = article.get_text(separator=' ', strip=True)
            else:
                paragraphs = soup.find_all('p')
                text = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text()) > 20])
            
            # Limit snippet size
            snippet = text[:500] + "..." if len(text) > 500 else text
            
            return {
                "title": title.strip(),
                "content": text.strip(),
                "snippet": snippet.strip(),
                "link": url,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
        except Exception as e:
            print(f"Scraper Error for {url}: {e}")
            return None

scraper = Scraper()
