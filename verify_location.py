
import requests
import json

def test_search(query, ai_mode=False):
    url = "http://127.0.0.1:5001/api/search"
    payload = {
        "query": query,
        "ai_mode": ai_mode
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"\nQuery: {query}")
        print(f"Detected Location: {data.get('mode', {}).get('detected_location', 'None')}")
        for i, result in enumerate(data.get("results", [])[:5]):
            print(f"{i+1}. {result['title']} (Location: {result.get('location', 'N/A')}, Final Score: {result['final_score']})")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    print("Testing Location Weighting...")
    
    # Test 1: Query with location
    test_search("earthquake in bihar")
    
    # Test 2: Query with another location
    test_search("flood in nepal")
    
    # Test 3: Query without location
    test_search("how to make pasta")
