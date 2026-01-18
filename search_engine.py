import math
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity

CUSTOM_STOP_WORDS = list(ENGLISH_STOP_WORDS) + [
    'said', 'says', 'reported', 'according', 'also', 'would', 'could',
    'news', 'report', 'reports', 'breaking', 'update', 'updates',
    'today', 'yesterday', 'week', 'month', 'year', 'years',
    'new', 'latest', 'recent', 'just', 'now', 'currently',
    'people', 'officials', 'government', 'sources', 'confirmed'
]


class SearchEngine:
    def __init__(self, data):
        self.data = data
        self.vectorizer = None
        self.tfidf_matrix = None
        self._build_index()

    def _build_index(self):
        if self.data.empty:
            return
        
        corpus = (self.data['title'] + " " + self.data['content']).tolist()
        
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words=CUSTOM_STOP_WORDS,
            ngram_range=(1, 2),
            max_features=10000
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query, mode="Standard", top_k=10):
        if self.data.empty or not query or self.vectorizer is None:
            return pd.DataFrame()

        query_vector = self.vectorizer.transform([query.lower()])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        results = self.data.copy()
        results['relevance_score'] = similarities
        results = results[results['relevance_score'] > 0]
        results = results.drop_duplicates(subset=['title'], keep='first')
        
        if len(results) > 0 and results['relevance_score'].max() > 0:
            results['relevance_score'] = results['relevance_score'] / results['relevance_score'].max()

        if mode == "Emergency":
            results = results[results['trust'] >= 0.7]
            results['final_score'] = results.apply(self._emergency_score, axis=1)
        else:
            results['final_score'] = results.apply(self._standard_score, axis=1)

        return results.sort_values(by='final_score', ascending=False).head(top_k)

    def _standard_score(self, row):
        return (row['relevance_score'] * 0.85) + (row['trust'] * 0.15)

    def _emergency_score(self, row):
        max_date = self.data['timestamp'].max()
        days_old = (max_date - row['timestamp']).days
        freshness = math.exp(-0.05 * max(0, days_old))
        sensational_penalty = row.get('sensational_score', 0) * 0.4

        return (row['relevance_score'] * 0.35) + \
               (freshness * 0.30) + \
               (row['trust'] * 0.35) - \
               sensational_penalty
