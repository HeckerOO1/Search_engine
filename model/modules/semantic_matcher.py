"""Semantic Matcher Module.

Uses Word2Vec embeddings for semantic similarity matching.
Handles emergency keyword expansion and semantic relevance scoring.
"""

import numpy as np
from typing import Optional, List
from config import EMERGENCY_KEYWORDS

# Global model cache
_word2vec_model = None


def get_word2vec_model():
    """
    Lazy load Word2Vec model and cache it.
    Uses GloVe 50-dimensional vectors for good performance.
    
    Returns:
        Loaded Word2Vec model or None if loading fails
    """
    global _word2vec_model
    
    if _word2vec_model is not None:
        return _word2vec_model
    
    try:
        import gensim.downloader as api
        print("Loading Word2Vec model (first time only, ~70MB)...")
        # Use GloVe 50d for good balance of speed and accuracy
        # Alternative: 'glove-wiki-gigaword-100' for better accuracy
        _word2vec_model = api.load('glove-wiki-gigaword-50')
        print(f"Word2Vec model loaded: {len(_word2vec_model)} words in vocabulary")
        return _word2vec_model
    except Exception as e:
        print(f"Warning: Could not load Word2Vec model: {e}")
        print("Semantic matching will be disabled. Install with: pip install gensim")
        return None


def calculate_word_similarity(word1: str, word2: str) -> float:
    """
    Calculate similarity between two words using Word2Vec.
    
    Args:
        word1: First word
        word2: Second word
        
    Returns:
        Similarity score (0-1), or 0 if words not in vocabulary
    """
    model = get_word2vec_model()
    if model is None:
        return 0.0
    
    try:
        word1 = word1.lower()
        word2 = word2.lower()
        
        # Check if both words are in vocabulary
        if word1 not in model or word2 not in model:
            return 0.0
        
        # Calculate cosine similarity
        similarity = model.similarity(word1, word2)
        
        # Normalize to 0-1 range (similarity can be negative)
        return max(0.0, similarity)
    except Exception:
        return 0.0


def is_emergency_query_semantic(query: str, threshold: float = 0.6) -> bool:
    """
    Check if query is semantically similar to emergency keywords.
    Expands emergency detection beyond exact keyword matches.
    
    Args:
        query: User's search query
        threshold: Minimum similarity score to consider emergency (default: 0.6)
        
    Returns:
        True if query is semantically related to emergencies
        
    Examples:
        "severe flooding" -> True (flood synonym)
        "inundation warning" -> True (flood synonym)
        "heavy rain" -> False (not emergency-level)
    """
    model = get_word2vec_model()
    if model is None:
        return False
    
    query_words = query.lower().split()
    
    for word in query_words:
        if word not in model:
            continue
        
        for emergency_kw in EMERGENCY_KEYWORDS:
            if emergency_kw not in model:
                continue
            
            try:
                similarity = model.similarity(word, emergency_kw)
                if similarity > threshold:
                    return True
            except Exception:
                continue
    
    return False


def calculate_semantic_document_score(query: str, text: str) -> float:
    """
    Calculate semantic similarity between query and document text.
    Uses average word vectors and cosine similarity.
    
    Args:
        query: User's search query
        text: Document text (title + snippet)
        
    Returns:
        Semantic similarity score (0-1)
    """
    model = get_word2vec_model()
    if model is None:
        return 0.5  # Neutral score if Word2Vec unavailable
    
    try:
        # Tokenize and filter to vocabulary words
        query_words = [w.lower() for w in query.split() if w.lower() in model]
        text_words = [w.lower() for w in text.split() if w.lower() in model]
        
        if not query_words or not text_words:
            return 0.5  # Neutral if no vocabulary overlap
        
        # Get average word vectors
        query_vectors = [model[w] for w in query_words]
        text_vectors = [model[w] for w in text_words]
        
        query_vec = np.mean(query_vectors, axis=0)
        text_vec = np.mean(text_vectors, axis=0)
        
        # Calculate cosine similarity
        dot_product = np.dot(query_vec, text_vec)
        query_norm = np.linalg.norm(query_vec)
        text_norm = np.linalg.norm(text_vec)
        
        if query_norm == 0 or text_norm == 0:
            return 0.5
        
        similarity = dot_product / (query_norm * text_norm)
        
        # Normalize to 0-1 range
        return max(0.0, min(1.0, (similarity + 1) / 2))
    
    except Exception as e:
        return 0.5  # Neutral score on error


def expand_emergency_keywords(base_keywords: List[str], top_n: int = 3) -> List[str]:
    """
    Expand emergency keywords with semantically similar words.
    Useful for building comprehensive emergency detection.
    
    Args:
        base_keywords: Original emergency keywords
        top_n: Number of similar words to add per keyword
        
    Returns:
        Expanded list of keywords including semantically similar ones
    """
    model = get_word2vec_model()
    if model is None:
        return base_keywords
    
    expanded = set(base_keywords)
    
    for keyword in base_keywords:
        if keyword not in model:
            continue
        
        try:
            # Get most similar words
            similar_words = model.most_similar(keyword, topn=top_n)
            for word, score in similar_words:
                if score > 0.7:  # Only add highly similar words
                    expanded.add(word)
        except Exception:
            continue
    
    return list(expanded)


# Singleton instance for convenience
def test_semantic_matching():
    """Test semantic matching functionality."""
    print("\n=== Testing Semantic Matching ===")
    
    # Test word similarity
    pairs = [
        ("flood", "deluge"),
        ("earthquake", "temblor"),
        ("fire", "blaze"),
        ("weather", "forecast")
    ]
    
    for w1, w2 in pairs:
        sim = calculate_word_similarity(w1, w2)
        print(f"Similarity('{w1}', '{w2}'): {sim:.3f}")
    
    # Test emergency detection
    queries = [
        "severe flooding in the area",
        "inundation warning issued",
        "heavy rain expected",
        "python programming tutorial"
    ]
    
    print("\nEmergency Detection:")
    for query in queries:
        is_emergency = is_emergency_query_semantic(query)
        print(f"'{query}': {'🚨 EMERGENCY' if is_emergency else '✓ Normal'}")


if __name__ == "__main__":
    test_semantic_matching()
