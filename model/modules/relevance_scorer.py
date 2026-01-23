"""Relevance Scorer Module.

Calculates query-to-document relevance using multiple signals:
1. BM25 with field weighting (60% title, 40% snippet)
2. Exact/partial/fuzzy term matching
3. Word2Vec semantic similarity

Combines all signals for robust relevance scoring.
"""

from rank_bm25 import BM25Okapi
from typing import Dict, List
import re


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance (edit distance) between two strings.
    Used for fuzzy matching to catch typos.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Number of edits (insertions, deletions, substitutions) needed
    """
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    
    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    
    return distances[-1]


def calculate_bm25_field_weighted(query: str, title: str, snippet: str) -> Dict[str, float]:
    """
    Calculate BM25 scores with field weighting.
    Title: 60% weight, Snippet: 40% weight
    
    Args:
        query: User's search query
        title: Document title
        snippet: Document snippet/description
        
    Returns:
        Dictionary with title_bm25, snippet_bm25, and weighted_bm25 scores
    """
    query_tokens = query.lower().split()
    
    # Calculate BM25 for title
    title_score = 0.0
    if title.strip():
        title_tokens = [title.lower().split()]
        try:
            bm25_title = BM25Okapi(title_tokens)
            title_score = bm25_title.get_scores(query_tokens)[0]
        except Exception:
            title_score = 0.0
    
    # Calculate BM25 for snippet
    snippet_score = 0.0
    if snippet.strip():
        snippet_tokens = [snippet.lower().split()]
        try:
            bm25_snippet = BM25Okapi(snippet_tokens)
            snippet_score = bm25_snippet.get_scores(query_tokens)[0]
        except Exception:
            snippet_score = 0.0
    
    # Weighted combination: 60% title, 40% snippet
    weighted_score = (title_score * 0.6) + (snippet_score * 0.4)
    
    return {
        "title_bm25": round(title_score, 3),
        "snippet_bm25": round(snippet_score, 3),
        "bm25_score": round(weighted_score, 3)
    }


def calculate_exact_partial_fuzzy_score(query: str, title: str, snippet: str) -> Dict[str, float]:
    """
    Calculate matching scores using exact, partial, and fuzzy matching.
    
    Scoring:
    - Exact match: 1.0 (full credit)
    - Partial match: 0.7 (substring match, e.g., "program" in "programming")
    - Fuzzy match: 0.5 (typo within 2 edits, e.g., "earthquke" → "earthquake")
    
    Args:
        query: User's search query
        title: Document title
        snippet: Document snippet
        
    Returns:
        Dictionary with match scores and details
    """
    query_terms = query.lower().split()
    title_words = title.lower().split()
    snippet_words = snippet.lower().split()
    
    title_matches = 0.0
    snippet_matches = 0.0
    
    for query_term in query_terms:
        # Check title
        title_match_value = 0.0
        for title_word in title_words:
            # Exact match
            if query_term == title_word:
                title_match_value = max(title_match_value, 1.0)
            # Partial match (substring)
            elif query_term in title_word or title_word in query_term:
                title_match_value = max(title_match_value, 0.7)
            # Fuzzy match (typo tolerance)
            elif levenshtein_distance(query_term, title_word) <= 2:
                title_match_value = max(title_match_value, 0.5)
        
        title_matches += title_match_value
        
        # Check snippet
        snippet_match_value = 0.0
        for snippet_word in snippet_words:
            # Exact match
            if query_term == snippet_word:
                snippet_match_value = max(snippet_match_value, 1.0)
            # Partial match
            elif query_term in snippet_word or snippet_word in query_term:
                snippet_match_value = max(snippet_match_value, 0.7)
            # Fuzzy match
            elif levenshtein_distance(query_term, snippet_word) <= 2:
                snippet_match_value = max(snippet_match_value, 0.5)
        
        snippet_matches += snippet_match_value
    
    # Normalize by number of query terms
    num_terms = len(query_terms)
    title_match_score = title_matches / num_terms if num_terms > 0 else 0.0
    snippet_match_score = snippet_matches / num_terms if num_terms > 0 else 0.0
    
    # Weighted combination: 60% title, 40% snippet
    combined_match_score = (title_match_score * 0.6) + (snippet_match_score * 0.4)
    
    return {
        "title_match": round(title_match_score, 3),
        "snippet_match": round(snippet_match_score, 3),
        "match_score": round(combined_match_score, 3)
    }


def calculate_semantic_score(query: str, title: str, snippet: str) -> float:
    """
    Calculate semantic similarity using Word2Vec.
    Falls back to neutral score if Word2Vec is unavailable.
    
    Args:
        query: User's search query
        title: Document title
        snippet: Document snippet
        
    Returns:
        Semantic similarity score (0-1)
    """
    try:
        from modules.semantic_matcher import calculate_semantic_document_score
        
        # Combine title and snippet with title weighted more
        # Title appears twice to give it more weight in semantic matching
        combined_text = f"{title} {title} {snippet}"
        
        semantic_score = calculate_semantic_document_score(query, combined_text)
        return round(semantic_score, 3)
    
    except Exception:
        # If Word2Vec unavailable, return neutral score
        return 0.5


def calculate_relevance_score(result: Dict, query: str) -> Dict:
    """
    Main function: Calculate comprehensive relevance score.
    
    Combines:
    - BM25 (50% weight) - Term frequency with saturation
    - Exact/Partial/Fuzzy matching (25% weight) - Catches variations
    - Semantic similarity (25% weight) - Word2Vec matching
    
    Args:
        result: Search result dictionary with 'title' and 'snippet' keys
        query: User's search query
        
    Returns:
        Dictionary with all relevance scores and final relevance_score
    """
    title = result.get("title", "")
    snippet = result.get("snippet", "")
    
    # 1. BM25 Score (50%)
    bm25_data = calculate_bm25_field_weighted(query, title, snippet)
    bm25_score = bm25_data["bm25_score"]
    
    # Normalize BM25 (typically ranges 0-5, normalize to 0-1)
    bm25_normalized = min(1.0, bm25_score / 5.0)
    
    # 2. Exact/Partial/Fuzzy Match Score (25%)
    match_data = calculate_exact_partial_fuzzy_score(query, title, snippet)
    match_score = match_data["match_score"]  # Already 0-1
    
    # 3. Semantic Score (25%)
    semantic_score = calculate_semantic_score(query, title, snippet)  # Already 0-1
    
    # Combine all signals with weights
    final_relevance = (
        bm25_normalized * 0.5 +
        match_score * 0.25 +
        semantic_score * 0.25
    )
    
    return {
        # BM25 scores
        "title_bm25": bm25_data["title_bm25"],
        "snippet_bm25": bm25_data["snippet_bm25"],
        "bm25_score": bm25_score,
        "bm25_normalized": round(bm25_normalized, 3),
        
        # Match scores
        "title_match": match_data["title_match"],
        "snippet_match": match_data["snippet_match"],
        "match_score": match_score,
        
        # Semantic score
        "semantic_score": semantic_score,
        
        # Final relevance
        "relevance_score": round(final_relevance, 3)
    }


# Test function
def test_relevance_scorer():
    """Test the relevance scoring system."""
    print("\n=== Testing Relevance Scorer ===\n")
    
    query = "earthquake california"
    
    test_cases = [
        {
            "title": "California Earthquake: 6.2 Magnitude Hits Bay Area",
            "snippet": "A major earthquake struck California today causing widespread damage"
        },
        {
            "title": "Weather Forecast for San Francisco",
            "snippet": "Sunny skies expected in the Bay Area this weekend"
        },
        {
            "title": "Earthquke in Californa",  # Typos
            "snippet": "Breaking news from the region"
        },
        {
            "title": "Seismic Activity Alert",
            "snippet": "Tremors detected in western United States"
        }
    ]
    
    for i, result in enumerate(test_cases, 1):
        print(f"Result {i}:")
        print(f"  Title: {result['title']}")
        print(f"  Snippet: {result['snippet'][:50]}...")
        
        scores = calculate_relevance_score(result, query)
        
        print(f"  BM25: {scores['bm25_normalized']:.3f} " +
              f"(title: {scores['title_bm25']:.2f}, snippet: {scores['snippet_bm25']:.2f})")
        print(f"  Match: {scores['match_score']:.3f} " +
              f"(title: {scores['title_match']:.2f}, snippet: {scores['snippet_match']:.2f})")
        print(f"  Semantic: {scores['semantic_score']:.3f}")
        print(f"  ⭐ FINAL RELEVANCE: {scores['relevance_score']:.3f}")
        print()


if __name__ == "__main__":
    test_relevance_scorer()
