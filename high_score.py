# high_score.py - High score system
import json
import os
from datetime import datetime

class HighScoreManager:
    def __init__(self):
        self.score_file = "high_scores.json"
        self.max_scores = 10  # Store top-10 records
        self.scores = self.load_scores()
    
    def load_scores(self):
        """Load records from file"""
        try:
            if os.path.exists(self.score_file):
                with open(self.score_file, 'r') as f:
                    data = json.load(f)
                    return data.get('scores', [])
            else:
                return []
        except Exception as e:
            print(f"Error loading scores: {e}")
            return []
    
    def save_scores(self):
        """Save records to file"""
        try:
            data = {
                'scores': self.scores,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.score_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving scores: {e}")
    
    def add_score(self, score, level, wave):
        """Add new result"""
        new_score = {
            'score': score,
            'level': level,
            'wave': wave,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        self.scores.append(new_score)
        
        
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Keep only top-N
        self.scores = self.scores[:self.max_scores]
        
        self.save_scores()
        
        # Return position in ranking (or None if didn't make it)
        for i, record in enumerate(self.scores):
            if (record['score'] == score and 
                record['level'] == level and 
                record['wave'] == wave and
                record['date'] == new_score['date']):
                return i + 1  # Position (1-based)
        
        return None
    
    def get_high_score(self):
        """Return best result"""
        if self.scores:
            return self.scores[0]['score']
        return 0
    
    def get_top_scores(self, count=5):
        """Return top-N results"""
        return self.scores[:count]
    
    def is_new_record(self, score):
        """Check if result is a new record"""
        if not self.scores:
            return True
        return score > self.scores[0]['score']
    
    def get_rank(self, score):
        """Return rank position for given score"""
        rank = 1
        for record in self.scores:
            if score > record['score']:
                return rank
            rank += 1
        return rank