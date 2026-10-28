"""VADER sentiment microservice using the starter's bundled lexicon."""
from pathlib import Path
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from flask import Flask, jsonify
nltk.data.path.insert(0, str(Path(__file__).resolve().parent))
app = Flask(__name__)
analyzer = SentimentIntensityAnalyzer()
@app.get('/')
def home():
    return jsonify(service='CarConnect VADER sentiment', status='ok')
@app.get('/analyze/<path:text>')
def analyze_sentiment(text):
    if len(text) > 5000:
        return jsonify(error='Text exceeds 5000 characters.'), 400
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    sentiment = 'positive' if compound >= 0.05 else 'negative' if compound <= -0.05 else 'neutral'
    return jsonify(sentiment=sentiment, scores=scores)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
