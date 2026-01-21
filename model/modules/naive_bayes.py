"""Naive Bayes Classifier Module.

Implements a Multinomial Naive Bayes classifier from scratch.
Uses log-probabilities to avoid underflow errors with long text.
This module is responsible for:
1. "Reading" the training data (Training)
2. "Learning" word probabilities (Vectorization & Priors)
3. "Predicting" the class of new text (Inference)
"""

import math
import re
from collections import defaultdict

class NaiveBayesClassifier:
    def __init__(self):
        self.classes = set()
        self.vocab = set()
        self.word_counts = defaultdict(lambda: defaultdict(int))
        self.class_counts = defaultdict(int)
        self.total_docs = 0
        self.class_priors = {}
        self.vocab_size = 0

    def tokenize(self, text: str) -> list:
        """Convert text to a list of lowercase alphanumeric tokens."""
        return re.findall(r'\w+', text.lower())

    def train(self, training_data: dict):
        """
        Train the classifier on a dictionary of labeled data.
        Format: {'emergency': ['text 1', 'text 2'], 'safe': [...]}
        """
        print("Training Naive Bayes Classifier...")
        
        # Reset state
        self.classes = set(training_data.keys())
        self.vocab = set()
        self.word_counts = defaultdict(lambda: defaultdict(int))
        self.class_counts = defaultdict(int)
        self.total_docs = 0
        
        # 1. Count everything
        for label, examples in training_data.items():
            self.class_counts[label] = len(examples)
            self.total_docs += len(examples)
            
            for text in examples:
                tokens = self.tokenize(text)
                self.vocab.update(tokens)
                for token in tokens:
                    self.word_counts[label][token] += 1
        
        self.vocab_size = len(self.vocab)
        
        # 2. Calculate Priors P(Class)
        for label in self.classes:
            self.class_priors[label] = math.log(self.class_counts[label] / self.total_docs)
            
        print(f"Training Complete. Types: {self.classes}, Vocab Size: {self.vocab_size}")

    def predict(self, text: str) -> dict:
        """
        Predict the class of a given text string.
        Returns dictionary with 'class' and 'confidence' scores.
        """
        tokens = self.tokenize(text)
        scores = {label: self.class_priors[label] for label in self.classes}
        
        for label in self.classes:
            # Total words in this class (for denominator)
            total_words_in_class = sum(self.word_counts[label].values())
            
            for token in tokens:
                # Laplace Smoothing: (count + 1) / (total + vocab_size)
                # We use +1 for the word count and +vocab_size for the total token count
                count = self.word_counts[label].get(token, 0) + 1
                prob = count / (total_words_in_class + self.vocab_size)
                scores[label] += math.log(prob)
        
        # Find winner
        best_label = max(scores, key=scores.get)
        
        # Normalize scores to look like percentages (Softmax approximation)
        # This is strictly for UI display, raw log scores are used for ranking
        try:
            # Shift scores to prevent overflow
            max_score = scores[best_label]
            exp_scores = {k: math.exp(v - max_score) for k, v in scores.items()}
            total_exp = sum(exp_scores.values())
            probs = {k: round(v / total_exp, 3) for k, v in exp_scores.items()}
        except:
            probs = {k: 0.0 for k in scores}
            probs[best_label] = 1.0

        return {
            "top_class": best_label,
            "probabilities": probs,
            "is_emergency": best_label == "emergency",
            "is_clickbait": best_label == "clickbait"
        }

# Singleton instance
classifier = NaiveBayesClassifier()
