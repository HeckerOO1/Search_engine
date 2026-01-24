from typing import List
import time
import requests
from bs4 import BeautifulSoup
import random

class DiscoveryLayer:
    # finds URLs to scrape by searching duckduckgo, bing, or yahoo
    
    def __init__(self):
        # different user agents so we dont look like a bot
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
    
    def discover_urls(self, query: str, num_results: int = 5) -> List[str]:
        # try to find URLs for the search query
        # tries duckduckgo first, then bing, then yahoo if those fail
        urls = []
        
        # first try duckduckgo (works best usually)
        try:
            print(f"Discovery (DuckDuckGo) attempting for query: {query}")
            urls = self._search_duckduckgo(query, num_results)
            
            if urls:
                print(f"Discovery (DuckDuckGo) found {len(urls)} URLs for query: {query}")
                return urls
        except Exception as e:
            print(f"Discovery (DuckDuckGo) Error: {e}")

        # duckduckgo failed, try bing
        try:
            print(f"Trying Fallback 1 Discovery (Bing) for query: {query}")
            urls = self._search_bing(query, num_results)
            
            if urls:
                print(f"Discovery (Bing) found {len(urls)} URLs for query: {query}")
                return urls
        except Exception as e:
            print(f"Discovery (Bing) Error: {e}")

        # bing also failed, last chance with yahoo
        try:
            print(f"Trying Fallback 2 Discovery (Yahoo) for query: {query}")
            urls = self._search_yahoo(query, num_results)
            
            if urls:
                print(f"Discovery (Yahoo) found {len(urls)} URLs for query: {query}")
                return urls
        except Exception as e:
            print(f"Discovery (Yahoo) Error: {e}")

        print(f"Discovery failed for all backends for query: {query}")
        return []
    
    def _search_duckduckgo(self, query: str, num_results: int) -> List[str]:
        # scrape duckduckgo HTML page for search results
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"DuckDuckGo returned status code: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = []
        
        # duckduckgo puts results in <a class="result__a"> tags
        for result in soup.find_all('a', class_='result__a', href=True):
            url = result['href']
            
            # skip duckduckgo's own links
            if url.startswith('http') and 'duckduckgo.com' not in url:
                if url not in urls:
                    urls.append(url)
                    if len(urls) >= num_results:
                        break
        
        return urls
    
    def _search_bing(self, query: str, num_results: int) -> List[str]:
        # scrape bing search results
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        
        search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Bing returned status code: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = []
        
        # bing results are in <li class="b_algo"> tags
        for result in soup.find_all('li', class_='b_algo'):
            a_tag = result.find('a', href=True)
            if a_tag:
                href = a_tag['href']
                if (href.startswith('http') and 
                    'bing.com' not in href and 
                    'microsoft.com' not in href):
                    
                    if href not in urls:
                        urls.append(href)
                        if len(urls) >= num_results:
                            break
        
        return urls
    
    def _search_yahoo(self, query: str, num_results: int) -> List[str]:
        # scrape yahoo search results
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        
        search_url = f"https://search.yahoo.com/search?p={query.replace(' ', '+')}"
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Yahoo returned status code: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        urls = []
        
        # yahoo wraps URLs in weird redirects sometimes
        for a in soup.find_all('a', href=True):
            href = a['href']
            
            # yahoo sometimes has /RU= in the URL, need to extract real URL
            if '/RU=' in href:
                try:
                    real_url = href.split('/RU=')[1].split('/RK=')[0]
                    from urllib.parse import unquote
                    href = unquote(real_url)
                except:
                    continue
            
            if (href.startswith('http') and 
                'yahoo.com' not in href and 
                'verizonmedia.com' not in href and
                'w3.org' not in href):
                
                if href not in urls:
                    urls.append(href)
                    if len(urls) >= num_results:
                        break
        
        return urls

# make one instance to use everywhere
discovery_layer = DiscoveryLayer()
