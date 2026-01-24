# yo this is spell checker stuff
# basically checks if user typed something wrong and fixes it
# using that levenshtein distance thing (fancy way to measure how different two words are)

import re
from collections import Counter

class SpellChecker:
    def __init__(self):
        self.vocabulary = set()  # gonna store all the words we know here
    
    def train(self, text_data: list):
        # ok so we gotta teach it what words are correct first
        # just throw all the text together and grab the words
        all_text = " ".join(text_data).lower()
        words = re.findall(r'\w+', all_text)  # regex magic to get words only
        self.vocabulary.update(words)
        print(f"SpellChecker learned {len(self.vocabulary)} unique words.")

    def levenshtein_distance(self, s1: str, s2: str) -> int:
        # this calculates how many changes needed to turn one word into another
        # like "cat" to "bat" is just 1 change, "cat" to "dog" is 3 changes
        # honestly this algorithm is kinda confusing but it works lol
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
        # tries to find the right word if user made typo
        # if word already correct, just return it
        word = word.lower()
        if word in self.vocabulary:
            return word

        best_match = word
        min_distance = float('inf')

        # only check words that are similar length, otherwise takes forever
        candidates = [w for w in self.vocabulary if abs(len(w) - len(word)) <= 2]
        
        if not candidates:
            return word  # cant fix it, just give up

        for candidate in candidates:
            dist = self.levenshtein_distance(word, candidate)
            
            # dont wanna fix words that are too different
            # short words get 2 mistakes max, long words get 3
            threshold = 2 if len(word) < 6 else 3
            
            if dist < min_distance and dist <= threshold:
                min_distance = dist
                best_match = candidate
        
        return best_match

    def correct_sentence(self, sentence: str) -> str:
        # fix all the words in a whole sentence
        words = re.findall(r'\w+', sentence.lower())
        corrected_words = []
        
        for word in words:
            corrected_words.append(self.correct(word))
            
        return " ".join(corrected_words)

# make one instance so we dont have to keep creating new ones
spell_checker = SpellChecker()
