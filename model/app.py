"""Emergency Search Engine - Flask Backend.

Main application server that combines all modules to provide
an emergency-aware search experience.
"""

from flask import Flask, render_template, request, jsonify
from modules.search_engine import search_engine
from modules.emergency_detector import detect_emergency_mode
from modules.truth_filter import calculate_trust_score
from modules.freshness_scorer import calculate_freshness_score
from modules.behavior_tracker import behavior_tracker
from config import STANDARD_MODE_WEIGHTS, EMERGENCY_MODE_WEIGHTS
from modules.spell_checker import spell_checker
from modules.naive_bayes import classifier
from modules.location_scorer import detect_location_in_query, calculate_location_score
import json
import os

app = Flask(__name__)

# Initialize AI Modules
def init_ai():
    try:
        data_path = os.path.join(os.path.dirname(__file__), 'data.json')
        with open(data_path, 'r') as f:
            data = json.load(f)
            
        if "training_data" in data:
            # Train Classifier
            classifier.train(data["training_data"])
            
            # Train Spell Checker
            # Combine all text for vocabulary
            all_text = []
            for category in data["training_data"].values():
                all_text.extend(category)
            spell_checker.train(all_text)
            print("AI Modules Initialized Successfully")
            
    except Exception as e:
        print(f"Warning: Failed to initialize AI modules: {e}")

# Run initialization
init_ai()


def calculate_final_score(result: dict, mode: str, target_location: str = None) -> dict:
    """
    Calculate the final ranking score for a search result.
    Combines trust, freshness, and behavior signals.
    """
    is_emergency = mode == "emergency"
    weights = EMERGENCY_MODE_WEIGHTS if is_emergency else STANDARD_MODE_WEIGHTS
    
    # Get trust score
    trust_data = calculate_trust_score(result)
    result.update(trust_data)
    
    # Get freshness score
    freshness_data = calculate_freshness_score(result, is_emergency)
    result.update(freshness_data)
    
    # Get behavior penalty
    pogo_penalty = behavior_tracker.get_penalty(result.get("link", ""))
    pogo_count = behavior_tracker.get_pogo_count(result.get("link", ""))
    
    # Calculate weighted final score
    # Popularity is simulated here - in production this would come from actual data
    popularity_score = 0.5  # Neutral popularity for now
    
    if target_location:
        # IF location is detected: use location weight
        location_score = calculate_location_score(result, target_location)
        result["location_score"] = location_score
        
        final_score = (
            result["freshness_score"] * weights["freshness"] +
            result["trust_score"] * weights["trust"] +
            popularity_score * weights["popularity"] +
            location_score * weights["location"] -
            pogo_penalty
        )
    else:
        # ELSE: use original weights (ignore location weight)
        # We need to re-normalize weights to 1.0 since location weight is 0
        total_non_loc_weight = weights["freshness"] + weights["trust"] + weights["popularity"]
        factor = 1.0 / total_non_loc_weight
        
        final_score = (
            (result["freshness_score"] * weights["freshness"] * factor) +
            (result["trust_score"] * weights["trust"] * factor) +
            (popularity_score * weights["popularity"] * factor) -
            pogo_penalty
        )
    
    result["final_score"] = round(max(0, final_score), 3)
    result["pogo_count"] = pogo_count
    result["pogo_penalty"] = pogo_penalty
    
    return result


def rank_results(results: list, mode: str, target_location: str = None) -> list:
    """Rank results by final score."""
    # Calculate scores for all results
    scored_results = [calculate_final_score(r, mode, target_location) for r in results]
    
    # Sort by final score (descending)
    scored_results.sort(key=lambda x: x["final_score"], reverse=True)
    
    return scored_results


@app.route("/")
def index():
    """Serve the main search page."""
    return render_template("index.html")


@app.route("/api/search", methods=["POST"])
def search():
    """Execute a search with emergency detection and result ranking."""
    data = request.get_json()
    query = data.get("query", "").strip()
    force_emergency = data.get("force_emergency", False)
    
    if not query:
        return jsonify({"error": "Query is required", "results": []})
    
    # Detect emergency mode (or use forced mode)
    if force_emergency:
        mode_info = {"mode": "emergency", "triggers": ["Manual activation"]}
        mode = "emergency"
    else:
        # Check for AI Mode
        use_ai = data.get("ai_mode", False)
        
        if use_ai:
            # 1. Auto-correct spelling
            original_query = query
            query = spell_checker.correct_sentence(query)
            
            # 2. AI Classification for Mode
            prediction = classifier.predict(query)
            
            if prediction["is_emergency"]:
                mode = "emergency"
            else:
                mode = "standard"
                
            mode_info = {
                "mode": mode,
                "triggers": [f"AI Confidence: {prediction['probabilities'].get('emergency', 0)}"],
                "ai_enabled": True,
                "original_query": original_query if original_query != query else None,
                "corrected_query": query
            }
        else:
            # Standard Heuristic Detection
            mode_info = detect_emergency_mode(query)
            mode = mode_info["mode"]
    
    # Execute search (use emergency search for emergency mode)
    if mode == "emergency":
        search_results = search_engine.search_emergency(query)
    else:
        search_results = search_engine.search(query)
    
    if search_results.get("error"):
        return jsonify({
            "error": search_results["error"],
            "results": [],
            "mode": mode_info
        })
    
    # Detect location for ranking boost
    target_location = detect_location_in_query(query)
    if target_location:
        mode_info["detected_location"] = target_location

    # Rank results with our scoring algorithm
    ranked_results = rank_results(search_results["results"], mode, target_location)
    
    return jsonify({
        "results": ranked_results,
        "mode": mode_info,
        "total_results": search_results["total_results"],
        "search_time": search_results.get("search_time", 0),
        "query": query
    })


@app.route("/api/feedback", methods=["POST"])
def feedback():
    """Record user behavior feedback."""
    data = request.get_json()
    action = data.get("action")
    url = data.get("url")
    query = data.get("query", "")
    
    if action == "click":
        result = behavior_tracker.record_click(url, query)
        return jsonify(result)
    
    elif action == "return":
        result = behavior_tracker.record_return(url)
        return jsonify(result)
    
    return jsonify({"error": "Invalid action"})


@app.route("/api/stats", methods=["GET"])
def stats():
    """Get behavior tracking statistics."""
    return jsonify(behavior_tracker.get_stats())


if __name__ == "__main__":
    print("=" * 50)
    print("Emergency Search Engine")
    print("=" * 50)
    print("Starting server at http://127.0.0.1:5001")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    app.run(debug=True, port=5001)
