class FeedbackLoop:
    def __init__(self):
        self.scores = {}

    def record(self, article_id, action):
        if article_id not in self.scores:
            self.scores[article_id] = 0.0

        if action == 'click_good':
            self.scores[article_id] += 0.05
        elif action == 'pogo_stick':
            self.scores[article_id] -= 0.1
        elif action == 'report_fake':
            self.scores[article_id] -= 0.5

    def get_score(self, article_id):
        return self.scores.get(article_id, 0.0)
