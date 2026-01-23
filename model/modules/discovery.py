from duckduckgo_search import DDGS
from googlesearch import search as gsearch
from typing import List
import time
import requests
from bs4 import BeautifulSoup
import random

class DiscoveryLayer:
    """Uses a discovery tool to find relevant URLs for deep scraping."""
    
    def discover_urls(self, query: str, num_results: int = 5) -> List[str]:
        """
        Find candidate URLs for a query.
        Tries multiple backends for robustness.
        """
        urls = []
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        headers = {'User-Agent': random.choice(user_agents)}
        
        # 1. Try DuckDuckGo (Primary)
        try:
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(query, max_results=num_results))
                urls = [item['href'] for item in raw_results if 'href' in item]
            
            if urls:
                print(f"Discovery (DuckDuckGo) found {len(urls)} URLs for query: {query}")
                return urls
        except Exception as e:
            print(f"Discovery (DuckDuckGo) Error: {e}")

        # 2. Try Google Search (Fallback 1)
        try:
            print(f"Trying Fallback 1 Discovery (Google) for query: {query}")
            g_results = gsearch(query, num_results=num_results)
            urls = list(g_results)
            
            if urls:
                print(f"Discovery (Google) found {len(urls)} URLs for query: {query}")
                return urls
        except Exception as e:
            print(f"Discovery (Google) Error: {e}")

        # 3. Try Brave Search (Fallback 2 - Direct Scraping)
        try:
            print(f"Trying Fallback 2 Discovery (Brave) for query: {query}")
            search_url = f"https://search.brave.com/search?q={query.replace(' ', '+')}"
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if (href.startswith('http') and 
                        'brave.com' not in href and 
                        'google.com' not in href and 
                        'microsoft.com' not in href and
                        'w3.org' not in href):
                        
                        if href not in urls:
                            urls.append(href)
                            if len(urls) >= num_results:
                                break
            
            if urls:
                print(f"Discovery (Brave) found {len(urls)} URLs for query: {query}")
                return urls
        except Exception as e:
            print(f"Discovery (Brave) Error: {e}")
            
        # 4. Try Bing (Fallback 3 - Direct Scraping)
        try:
            print(f"Trying Fallback 3 Discovery (Bing) for query: {query}")
            search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if (href.startswith('http') and 'bing.com' not in href and 'microsoft.com' not in href):
                        if href not in urls:
                            urls.append(href)
                            if len(urls) >= num_results: break
            if urls:
                print(f"Discovery (Bing) found {len(urls)} URLs for query: {query}")
                return urls
        except Exception as e:
            print(f"Discovery (Bing) Error: {e}")

        # 5. Try Yahoo (Fallback 4 - Direct Scraping)
        try:
            print(f"Trying Fallback 4 Discovery (Yahoo) for query: {query}")
            search_url = f"https://search.yahoo.com/search?p={query.replace(' ', '+')}"
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Yahoo results are often in <a> tags with class containing 'd-flex' or similar
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if (href.startswith('http') and 'yahoo.com' not in href):
                        if href not in urls:
                            urls.append(href)
                            if len(urls) >= num_results: break
            if urls:
                print(f"Discovery (Yahoo) found {len(urls)} URLs for query: {query}")
                return urls
        except Exception as e:
            print(f"Discovery (Yahoo) Error: {e}")

        # 6. Try Ecosia (Fallback 5 - Direct Scraping)
        try:
            print(f"Trying Fallback 5 Discovery (Ecosia) for query: {query}")
            search_url = f"https://www.ecosia.org/search?q={query.replace(' ', '+')}"
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if (href.startswith('http') and 'ecosia.org' not in href):
                        if href not in urls:
                            urls.append(href)
                            if len(urls) >= num_results: break
            if urls:
                print(f"Discovery (Ecosia) found {len(urls)} URLs for query: {query}")
                return urls
        except Exception as e:
            print(f"Discovery (Ecosia) Error: {e}")

        # 7. Try Ask.com (Fallback 6 - Direct Scraping)
        try:
            print(f"Trying Fallback 6 Discovery (Ask.com) for query: {query}")
            search_url = f"https://www.ask.com/web?q={query.replace(' ', '+')}"
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if (href.startswith('http') and 'ask.com' not in href):
                        if href not in urls:
                            urls.append(href)
                            if len(urls) >= num_results: break
            if urls:
                print(f"Discovery (Ask.com) found {len(urls)} URLs for query: {query}")
                return urls
        except Exception as e:
            print(f"Discovery (Ask.com) Error: {e}")

        # 8. Try Swisscows (Fallback 7 - Direct Scraping)
        try:
            print(f"Trying Fallback 7 Discovery (Swisscows) for query: {query}")
            search_url = f"https://swisscows.com/en/web?query={query.replace(' ', '+')}"
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if (href.startswith('http') and 'swisscows.com' not in href):
                        if href not in urls:
                            urls.append(href)
                            if len(urls) >= num_results: break
            if urls:
                print(f"Discovery (Swisscows) found {len(urls)} URLs for query: {query}")
                return urls
        except Exception as e:
            print(f"Discovery (Swisscows) Error: {e}")
            
        print(f"Discovery failed for all backends for query: {query}")
        return []

discovery_layer = DiscoveryLayer()
