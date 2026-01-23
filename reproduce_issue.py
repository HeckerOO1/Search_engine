from modules.discovery import discovery_layer
from modules.naive_bayes import classifier
import sys
import os
import json

# Add model directory to path so we can import modules
sys.path.append(os.path.join(os.getcwd(), 'model'))

def init_classifier():
    data_path = os.path.join(os.getcwd(), 'model', 'data.json')
    with open(data_path, 'r') as f:
        data = json.load(f)
    classifier.train(data["training_data"])

def test_ai(query):
    print(f"\n--- Testing AI Classification for: {query} ---")
    prediction = classifier.predict(query)
    print(f"Is Emergency: {prediction['is_emergency']}")
    print(f"Probabilities: {prediction['probabilities']}")

def test_search(query):
    print(f"\n--- Testing Discovery for: {query} ---")
    urls = discovery_layer.discover_urls(query)
    print(f"URLs found: {len(urls)}")
    for url in urls[:3]: # Show first 3
        print(f" - {url}")

if __name__ == "__main__":
    init_classifier()
    
    # Test AI Detection
    test_ai("wildfire shelters location")
    test_ai("how to make pasta")
    test_ai("earthquake near me")
    
    # Test Discovery Fallback
    test_search("emergency help earthquake")
