"""Spell Checker Module.

Implements a custom Levenshtein Distance algorithm to find and fix typos
in search queries. This is a "from scratch" implementation of a classic
dynamic programming algorithm.
"""

import re
from collections import Counter

class SpellChecker:
    def __init__(self):
        self.vocabulary = set()
    
    def train(self, text_data: list):
        """
        Build vocabulary from a list of text strings.
        Populates the known words set.
        """
        all_text = " ".join(text_data).lower()
        # Simple tokenization: keep only letters and numbers
        words = re.findall(r'\w+', all_text)
        self.vocabulary.update(words)
        print(f"SpellChecker learned {len(self.vocabulary)} unique words.")

    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate the Levenshtein distance between two strings.
        This is the minimum number of single-character edits (insertions, deletions, or substitutions)
        required to change one word into the other.
        """
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    def correct(self, word: str) -> str:
        """
        Find the closest matching word in the vocabulary.
        Returns the original word if it matches or if no close match is found.
        """
        word = word.lower()
        if word in self.vocabulary:
            return word

        best_match = word
        min_distance = float('inf')

        # Limit search to words of similar length for performance
        candidates = [w for w in self.vocabulary if abs(len(w) - len(word)) <= 2]
        
        if not candidates:
            return word

        for candidate in candidates:
            dist = self.levenshtein_distance(word, candidate)
            
            # Threshold: Allow max 2 errors for short words, 3 for long
            threshold = 2 if len(word) < 6 else 3
            
            if dist < min_distance and dist <= threshold:
                min_distance = dist
                best_match = candidate
        
        return best_match

    def correct_sentence(self, sentence: str) -> str:
        """Correct all words in a sentence."""
        words = re.findall(r'\w+', sentence.lower())
        corrected_words = []
        
        for word in words:
            corrected_words.append(self.correct(word))
            
        return " ".join(corrected_words)

# Singleton instance
spell_checker = SpellChecker()
