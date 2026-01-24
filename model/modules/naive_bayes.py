# naive bayes classifier - sounds fancy but its pretty simple actually
# basically teaches itself to recognize different types of text
# like is this an emergency query or just normal search or clickbait etc
# uses math probability stuff but we use logs so numbers dont get too tiny

import math
import re
from collections import defaultdict

class NaiveBayesClassifier:
    def __init__(self):
        self.classes = set()  # like emergency, safe, clickbait etc
        self.vocab = set()  # all words it knows
        self.word_counts = defaultdict(lambda: defaultdict(int))  # how many times each word appears in each category
        self.class_counts = defaultdict(int)  # how many examples of each type
        self.total_docs = 0
        self.class_priors = {}  # probability of each class
        self.vocab_size = 0

    def tokenize(self, text: str) -> list:
        # just breaks text into words, nothing fancy
        return re.findall(r'\w+', text.lower())

    def train(self, training_data: dict):
        # ok so this is where we teach it
        # give it examples like {'emergency': ['fire!', 'help!'], 'safe': ['pizza recipe']}
        print("Training Naive Bayes Classifier...")
        
        # clear everything first
        self.classes = set(training_data.keys())
        self.vocab = set()
        self.word_counts = defaultdict(lambda: defaultdict(int))
        self.class_counts = defaultdict(int)
        self.total_docs = 0
        
        # step 1: count all the words and stuff
        for label, examples in training_data.items():
            self.class_counts[label] = len(examples)
            self.total_docs += len(examples)
            
            for text in examples:
                tokens = self.tokenize(text)
                self.vocab.update(tokens)
                for token in tokens:
                    self.word_counts[label][token] += 1
        
        self.vocab_size = len(self.vocab)
        
        # step 2: calculate base probabilities for each category
        for label in self.classes:
            self.class_priors[label] = math.log(self.class_counts[label] / self.total_docs)
            
        print(f"Training Complete. Types: {self.classes}, Vocab Size: {self.vocab_size}")

    def predict(self, text: str) -> dict:
        # figure out what category this text belongs to
        # returns a dict with the answer and how confident it is
        tokens = self.tokenize(text)
        scores = {label: self.class_priors[label] for label in self.classes}
        
        for label in self.classes:
            # count total words in this category
            total_words_in_class = sum(self.word_counts[label].values())
            
            for token in tokens:
                # laplace smoothing - fancy name for adding 1 to everything
                # so we dont get zero probabilities for words we havent seen
                count = self.word_counts[label].get(token, 0) + 1
                prob = count / (total_words_in_class + self.vocab_size)
                scores[label] += math.log(prob)  # using logs so numbers stay manageable
        
        # whoever got highest score wins
        best_label = max(scores, key=scores.get)
        
        # convert scores to percentages so it looks nicer in UI
        # this part is just for show, actual prediction uses raw scores
        try:
            max_score = scores[best_label]
            exp_scores = {k: math.exp(v - max_score) for k, v in scores.items()}
            total_exp = sum(exp_scores.values())
            probs = {k: round(v / total_exp, 3) for k, v in exp_scores.items()}
        except:
            # if math breaks just say 100% for winner
            probs = {k: 0.0 for k in scores}
            probs[best_label] = 1.0

        return {
            "top_class": best_label,
            "probabilities": probs,
            "is_emergency": best_label == "emergency",
            "is_clickbait": best_label == "clickbait"
        }

# just make one and reuse it
classifier = NaiveBayesClassifier()
