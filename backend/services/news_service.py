import requests
import os
from datetime import datetime, timedelta

class NewsService:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY', 'h8iwfrj3OeAQj3zMrRngoqjlwMWef6P5ITs2HAS1')
        self.base_url = "https://api.thenewsapi.com/v1/news"
        
        # Keywords to filter out inappropriate content
        self.inappropriate_keywords = [
            'porn', 'adult', 'xxx', 'erotic', 'sex', 'nude', 'nudity', 
            'explicit', 'pornographic', 'mature', 'violence', 'gore'
        ]

    def _is_appropriate_content(self, article):
        """Check if the article content is appropriate."""
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        
        return not any(keyword in title or keyword in description 
                      for keyword in self.inappropriate_keywords)

    def get_top_stories(self, page=1, categories=None):
        """Get top stories with optional category filtering."""
        try:
            params = {
                'api_token': self.api_key,
                'page': page,
                'language': 'en',
                'limit': 12  # Number of articles per page
            }
            
            if categories:
                params['categories'] = ','.join(categories)

            response = requests.get(f"{self.base_url}/top", params=params)
            if response.status_code != 200:
                print(f"Error from News API: {response.text}")
                return []

            data = response.json()
            articles = []
            
            for article in data.get('data', []):
                if self._is_appropriate_content(article):
                    formatted_article = {
                        'title': article.get('title'),
                        'description': article.get('description'),
                        'url': article.get('url'),
                        'image_url': article.get('image_url'),
                        'published_at': article.get('published_at'),
                        'source': article.get('source'),
                        'categories': article.get('categories', []),
                        'snippet': article.get('snippet')
                    }
                    articles.append(formatted_article)

            return {
                'articles': articles,
                'meta': {
                    'found': data.get('meta', {}).get('found', 0),
                    'returned': data.get('meta', {}).get('returned', 0),
                    'limit': data.get('meta', {}).get('limit', 12),
                    'page': data.get('meta', {}).get('page', 1)
                }
            }
        except Exception as e:
            print(f"Error fetching top stories: {e}")
            return {'articles': [], 'meta': {}}

    def search_magazines(self, query, page=1):
        """Search for magazine articles."""
        try:
            params = {
                'api_token': self.api_key,
                'search': query,
                'page': page,
                'language': 'en',
                'limit': 12,
                'sort': 'relevance_score'
            }

            response = requests.get(f"{self.base_url}/all", params=params)
            if response.status_code != 200:
                print(f"Error from News API: {response.text}")
                return []

            data = response.json()
            articles = []
            
            for article in data.get('data', []):
                if self._is_appropriate_content(article):
                    formatted_article = {
                        'title': article.get('title'),
                        'description': article.get('description'),
                        'url': article.get('url'),
                        'image_url': article.get('image_url'),
                        'published_at': article.get('published_at'),
                        'source': article.get('source'),
                        'categories': article.get('categories', []),
                        'snippet': article.get('snippet')
                    }
                    articles.append(formatted_article)

            return {
                'articles': articles,
                'meta': {
                    'found': data.get('meta', {}).get('found', 0),
                    'returned': data.get('meta', {}).get('returned', 0),
                    'limit': data.get('meta', {}).get('limit', 12),
                    'page': data.get('meta', {}).get('page', 1)
                }
            }
        except Exception as e:
            print(f"Error searching magazines: {e}")
            return {'articles': [], 'meta': {}}

    def get_categories(self):
        """Get available news categories."""
        return [
            'general', 'business', 'entertainment', 'health', 
            'science', 'sports', 'technology', 'politics'
        ]
