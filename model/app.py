# main flask app for divyadhrishti search engine
# this is where everything comes together - search, AI, emergency detection etc

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

# gotta setup the AI stuff when server starts
def init_ai():
    try:
        data_path = os.path.join(os.path.dirname(__file__), 'data.json')
        with open(data_path, 'r') as f:
            data = json.load(f)
            
        if "training_data" in data:
            # teach the classifier first
            classifier.train(data["training_data"])
            
            # then teach spell checker
            # just grab all the text and throw it in
            all_text = []
            for category in data["training_data"].values():
                all_text.extend(category)
            spell_checker.train(all_text)
            print("AI Modules Initialized Successfully")
            
    except Exception as e:
        print(f"Warning: Failed to initialize AI modules: {e}")

# run this when server starts
init_ai()


def calculate_final_score(result: dict, mode: str, target_location: str = None) -> dict:
    # this is where we figure out how good each search result is
    # combines trust, how fresh it is, and if people keep bouncing back from it
    is_emergency = mode == "emergency"
    weights = EMERGENCY_MODE_WEIGHTS if is_emergency else STANDARD_MODE_WEIGHTS
    
    # check how trustworthy the source is
    trust_data = calculate_trust_score(result)
    result.update(trust_data)
    
    # check how fresh/recent the content is
    freshness_data = calculate_freshness_score(result, is_emergency)
    result.update(freshness_data)
    
    # check if people keep coming back (pogo-sticking = bad result)
    pogo_penalty = behavior_tracker.get_penalty(result.get("link", ""))
    pogo_count = behavior_tracker.get_pogo_count(result.get("link", ""))
    
    # now calculate the final score with all the weights
    # popularity is just set to 0.5 for now, would need real click data for this
    popularity_score = 0.5
    
    if target_location:
        # if user searched for a specific location, factor that in
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
        # no location mentioned, so redistribute those weights to other factors
        # gotta make sure everything still adds up to 1.0
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
    # sort all results by their scores, best ones first
    scored_results = [calculate_final_score(r, mode, target_location) for r in results]
    
    # sort em highest to lowest
    scored_results.sort(key=lambda x: x["final_score"], reverse=True)
    
    return scored_results


@app.route("/")
def index():
    # just show the main search page
    return render_template("index.html")


@app.route("/api/search", methods=["POST"])
def search():
    # main search endpoint - this is where the magic happens
    data = request.get_json()
    query = data.get("query", "").strip()
    force_emergency = data.get("force_emergency", False)
    
    if not query:
        return jsonify({"error": "Query is required", "results": []})
    
    # figure out if this is emergency mode or not
    if force_emergency:
        mode_info = {"mode": "emergency", "triggers": ["Manual activation"]}
        mode = "emergency"
    else:
        # check if AI mode is turned on
        use_ai = data.get("ai_mode", False)
        
        if use_ai:
            # first fix any spelling mistakes
            original_query = query
            query = spell_checker.correct_sentence(query)
            
            # then let AI decide if its emergency or not
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
            # AI mode off, use basic keyword detection
            mode_info = detect_emergency_mode(query)
            mode = mode_info["mode"]
    
    # actually do the search now
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
    
    # check if they mentioned a location so we can boost local results
    target_location = detect_location_in_query(query)
    if target_location:
        mode_info["detected_location"] = target_location

    # rank all the results using our fancy algorithm
    ranked_results = rank_results(search_results["results"], mode, target_location)
    
    return jsonify({
        "results": ranked_results,
        "mode": mode_info,
        "total_results": search_results["total_results"],
        "search_time": search_results.get("search_time", 0),
        "query": query,
        "source": search_results.get("source"),
        "message": search_results.get("message")
    })


@app.route("/api/feedback", methods=["POST"])
def feedback():
    # tracks when user clicks stuff or comes back quickly (pogo-sticking)
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
    # just returns some stats about user behavior
    return jsonify(behavior_tracker.get_stats())


if __name__ == "__main__":
    print("=" * 50)
    print("DivyaDhrishti")
    print("=" * 50)
    print("Starting server at http://127.0.0.1:5001")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    app.run(debug=True, port=5001)
