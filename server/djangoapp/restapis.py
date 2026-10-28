"""Explicit, bounded HTTP calls to the dealer and sentiment services."""
from urllib.parse import quote
import requests
from django.conf import settings
def get_request(endpoint):
    response = requests.get(f'{settings.BACKEND_URL}/{endpoint.lstrip("/")}', timeout=15)
    response.raise_for_status()
    return response.json()
def analyze_review_sentiments(text):
    response = requests.get(f'{settings.SENTIMENT_URL}/analyze/{quote(text, safe="")}', timeout=15)
    response.raise_for_status()
    return response.json()['sentiment']
def post_review(data):
    response = requests.post(f'{settings.BACKEND_URL}/insert_review', json=data, timeout=15)
    response.raise_for_status()
    return response.json()
