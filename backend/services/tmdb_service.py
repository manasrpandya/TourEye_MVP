from tmdbv3api import TMDb, Movie, Genre, Discover, TV
import requests
import os
import re

class TMDBService:
    def __init__(self):
        self.tmdb = TMDb()
        self.api_key = os.getenv('TMDB_API_KEY', 'e889297f45708465dad1aae3216b1c44')
        self.tmdb.api_key = self.api_key
        self.tmdb.language = 'en'
        self.movie = Movie()
        self.genre = Genre()
        self.discover = Discover()
        self.tv = TV()
        self.DOCUMENTARY_GENRE_ID = 99
        self.base_url = "https://api.themoviedb.org/3"
        
        # Keywords and patterns to filter out inappropriate content
        self.inappropriate_keywords = [
            'porn', 'adult', 'xxx', 'erotic', 'sex', 'nude', 'nudity', 
            'explicit', 'pornographic', 'mature'
        ]
        self.inappropriate_pattern = re.compile('|'.join(self.inappropriate_keywords), re.IGNORECASE)

    def get_movie_details(self, movie_id):
        try:
            movie = self.movie.details(movie_id)
            
            # Check if the content is appropriate
            if not self._is_appropriate_content({
                'title': getattr(movie, 'title', ''),
                'overview': getattr(movie, 'overview', '')
            }):
                raise Exception("Content not appropriate")
            
            return {
                'id': movie.id,
                'title': movie.title,
                'overview': movie.overview,
                'poster_path': f"https://image.tmdb.org/t/p/w500{movie.poster_path}" if movie.poster_path else None,
                'backdrop_path': f"https://image.tmdb.org/t/p/original{movie.backdrop_path}" if movie.backdrop_path else None,
                'release_date': movie.release_date,
                'vote_average': movie.vote_average,
                'genres': [genre.name for genre in movie.genres],
                'runtime': movie.runtime,
                'status': movie.status,
                'tagline': movie.tagline
            }
        except Exception as e:
            print(f"Error in get_movie_details: {e}")
            raise

    def get_movies(self, page=1):
        try:
            url = f"{self.base_url}/discover/movie"
            params = {
                'api_key': self.api_key,
                'sort_by': 'popularity.desc',
                'page': page,
                'language': 'en-US',
                'include_adult': False,  # Explicitly exclude adult content
                'certification_country': 'US',
                'certification.lte': 'PG-13'  # Only include up to PG-13 rated content
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error from TMDB API: {response.text}")
                return []
            
            data = response.json()
            formatted_movies = []
            
            for movie in data.get('results', []):
                try:
                    # Skip inappropriate content
                    if not self._is_appropriate_content(movie):
                        print(f"Filtered out inappropriate movie: {movie.get('title', 'Unknown')}")
                        continue
                        
                    formatted_movie = {
                        'id': movie.get('id', 0),
                        'title': movie.get('title', 'Unknown Title'),
                        'overview': movie.get('overview', 'No overview available'),
                        'poster_path': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else "/static/images/placeholder.jpg",
                        'backdrop_path': f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}" if movie.get('backdrop_path') else None,
                        'release_date': movie.get('release_date', 'Unknown'),
                        'vote_average': movie.get('vote_average', 0.0)
                    }
                    formatted_movies.append(formatted_movie)
                except Exception as e:
                    print(f"Error formatting movie: {e}")
                    continue
            
            return formatted_movies
        except Exception as e:
            print(f"Error fetching movies: {e}")
            return []

    def get_trending_movies(self):
        try:
            url = f"{self.base_url}/trending/movie/week"
            params = {
                'api_key': self.api_key,
                'language': 'en-US',
                'include_adult': False,
                'certification_country': 'US',
                'certification.lte': 'PG-13'
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error from TMDB API: {response.text}")
                return []
            
            data = response.json()
            formatted_movies = []
            
            for movie in data.get('results', [])[:8]:
                try:
                    # Skip inappropriate content
                    if not self._is_appropriate_content(movie):
                        print(f"Filtered out inappropriate trending movie: {movie.get('title', 'Unknown')}")
                        continue
                        
                    formatted_movie = {
                        'id': movie.get('id', 0),
                        'title': movie.get('title', 'Unknown Title'),
                        'overview': movie.get('overview', 'No overview available'),
                        'poster_path': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else "/static/images/placeholder.jpg",
                        'backdrop_path': f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}" if movie.get('backdrop_path') else None,
                        'release_date': movie.get('release_date', 'Unknown'),
                        'vote_average': movie.get('vote_average', 0.0)
                    }
                    formatted_movies.append(formatted_movie)
                except Exception as e:
                    print(f"Error formatting trending movie: {e}")
                    continue
            
            return formatted_movies
        except Exception as e:
            print(f"Error fetching trending movies: {e}")
            return []

    def get_series_details(self, series_id):
        try:
            series = self.tv.details(series_id)
            
            # Check if the content is appropriate
            if not self._is_appropriate_content({
                'title': getattr(series, 'name', ''),
                'overview': getattr(series, 'overview', '')
            }):
                raise Exception("Content not appropriate")
            
            return {
                'id': series.id,
                'title': series.name,
                'overview': series.overview,
                'poster_path': f"https://image.tmdb.org/t/p/w500{series.poster_path}" if series.poster_path else None,
                'backdrop_path': f"https://image.tmdb.org/t/p/original{series.backdrop_path}" if series.backdrop_path else None,
                'first_air_date': series.first_air_date,
                'vote_average': series.vote_average,
                'genres': [genre.name for genre in series.genres],
                'number_of_seasons': series.number_of_seasons,
                'status': series.status,
                'tagline': getattr(series, 'tagline', '')
            }
        except Exception as e:
            print(f"Error in get_series_details: {e}")
            raise

    def get_series(self, page=1):
        try:
            url = f"{self.base_url}/discover/tv"
            params = {
                'api_key': self.api_key,
                'sort_by': 'popularity.desc',
                'page': page,
                'language': 'en-US',
                'include_adult': False,
                'certification_country': 'US',
                'certification.lte': 'TV-PG'  # Using TV-PG rating for series
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error from TMDB API: {response.text}")
                return []
            
            data = response.json()
            formatted_series = []
            
            for series in data.get('results', []):
                try:
                    # Skip inappropriate content
                    if not self._is_appropriate_content({
                        'title': series.get('name', ''),
                        'overview': series.get('overview', '')
                    }):
                        print(f"Filtered out inappropriate series: {series.get('name', 'Unknown')}")
                        continue
                        
                    formatted_series_item = {
                        'id': series.get('id', 0),
                        'title': series.get('name', 'Unknown Title'),
                        'overview': series.get('overview', 'No overview available'),
                        'poster_path': f"https://image.tmdb.org/t/p/w500{series.get('poster_path')}" if series.get('poster_path') else "/static/images/placeholder.jpg",
                        'backdrop_path': f"https://image.tmdb.org/t/p/original{series.get('backdrop_path')}" if series.get('backdrop_path') else None,
                        'first_air_date': series.get('first_air_date', 'Unknown'),
                        'vote_average': series.get('vote_average', 0.0)
                    }
                    formatted_series.append(formatted_series_item)
                except Exception as e:
                    print(f"Error formatting series: {e}")
                    continue
            
            return formatted_series
        except Exception as e:
            print(f"Error fetching series: {e}")
            return []

    def get_trending_series(self):
        try:
            url = f"{self.base_url}/trending/tv/week"
            params = {
                'api_key': self.api_key,
                'language': 'en-US',
                'include_adult': False,
                'certification_country': 'US',
                'certification.lte': 'TV-PG'
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error from TMDB API: {response.text}")
                return []
            
            data = response.json()
            formatted_series = []
            
            for series in data.get('results', [])[:8]:
                try:
                    # Skip inappropriate content
                    if not self._is_appropriate_content({
                        'title': series.get('name', ''),
                        'overview': series.get('overview', '')
                    }):
                        print(f"Filtered out inappropriate trending series: {series.get('name', 'Unknown')}")
                        continue
                        
                    formatted_series_item = {
                        'id': series.get('id', 0),
                        'title': series.get('name', 'Unknown Title'),
                        'overview': series.get('overview', 'No overview available'),
                        'poster_path': f"https://image.tmdb.org/t/p/w500{series.get('poster_path')}" if series.get('poster_path') else "/static/images/placeholder.jpg",
                        'backdrop_path': f"https://image.tmdb.org/t/p/original{series.get('backdrop_path')}" if series.get('backdrop_path') else None,
                        'first_air_date': series.get('first_air_date', 'Unknown'),
                        'vote_average': series.get('vote_average', 0.0)
                    }
                    formatted_series.append(formatted_series_item)
                except Exception as e:
                    print(f"Error formatting trending series: {e}")
                    continue
            
            return formatted_series
        except Exception as e:
            print(f"Error fetching trending series: {e}")
            return []

    def get_popular_movies(self, page=1):
        try:
            url = f"{self.base_url}/discover/movie"
            params = {
                'api_key': self.api_key,
                'sort_by': 'popularity.desc',
                'page': page,
                'language': 'en-US',
                'include_adult': False,  # Explicitly exclude adult content
                'certification_country': 'US',
                'certification.lte': 'PG-13'  # Only include up to PG-13 rated content
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error from TMDB API: {response.text}")
                return []
            
            data = response.json()
            formatted_movies = []
            
            for movie in data.get('results', []):
                try:
                    # Skip inappropriate content
                    if not self._is_appropriate_content(movie):
                        print(f"Filtered out inappropriate movie: {movie.get('title', 'Unknown')}")
                        continue
                        
                    formatted_movie = {
                        'id': movie.get('id', 0),
                        'title': movie.get('title', 'Unknown Title'),
                        'overview': movie.get('overview', 'No overview available'),
                        'poster_path': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else "/static/images/placeholder.jpg",
                        'backdrop_path': f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}" if movie.get('backdrop_path') else None,
                        'release_date': movie.get('release_date', 'Unknown'),
                        'vote_average': movie.get('vote_average', 0.0)
                    }
                    formatted_movies.append(formatted_movie)
                except Exception as e:
                    print(f"Error formatting movie: {e}")
                    continue
            
            return formatted_movies
        except Exception as e:
            print(f"Error fetching popular movies: {e}")
            return []

    def get_popular_series(self, page=1):
        try:
            url = f"{self.base_url}/discover/tv"
            params = {
                'api_key': self.api_key,
                'sort_by': 'popularity.desc',
                'page': page,
                'language': 'en-US',
                'include_adult': False,
                'certification_country': 'US',
                'certification.lte': 'TV-PG'  # Using TV-PG rating for series
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error from TMDB API: {response.text}")
                return []
            
            data = response.json()
            formatted_series = []
            
            for series in data.get('results', []):
                try:
                    # Skip inappropriate content
                    if not self._is_appropriate_content({
                        'title': series.get('name', ''),
                        'overview': series.get('overview', '')
                    }):
                        print(f"Filtered out inappropriate series: {series.get('name', 'Unknown')}")
                        continue
                        
                    formatted_series_item = {
                        'id': series.get('id', 0),
                        'title': series.get('name', 'Unknown Title'),
                        'overview': series.get('overview', 'No overview available'),
                        'poster_path': f"https://image.tmdb.org/t/p/w500{series.get('poster_path')}" if series.get('poster_path') else "/static/images/placeholder.jpg",
                        'backdrop_path': f"https://image.tmdb.org/t/p/original{series.get('backdrop_path')}" if series.get('backdrop_path') else None,
                        'first_air_date': series.get('first_air_date', 'Unknown'),
                        'vote_average': series.get('vote_average', 0.0)
                    }
                    formatted_series.append(formatted_series_item)
                except Exception as e:
                    print(f"Error formatting series: {e}")
                    continue
            
            return formatted_series
        except Exception as e:
            print(f"Error fetching popular series: {e}")
            return []

    def search_movies(self, query, page=1):
        try:
            url = f"{self.base_url}/search/movie"
            params = {
                'api_key': self.api_key,
                'query': query,
                'page': page,
                'language': 'en-US',
                'include_adult': False,  # Explicitly exclude adult content
                'certification_country': 'US',
                'certification.lte': 'PG-13'  # Only include up to PG-13 rated content
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error from TMDB API: {response.text}")
                return []
            
            data = response.json()
            formatted_movies = []
            
            for movie in data.get('results', []):
                try:
                    # Skip inappropriate content
                    if not self._is_appropriate_content(movie):
                        print(f"Filtered out inappropriate movie: {movie.get('title', 'Unknown')}")
                        continue
                        
                    formatted_movie = {
                        'id': movie.get('id', 0),
                        'title': movie.get('title', 'Unknown Title'),
                        'overview': movie.get('overview', 'No overview available'),
                        'poster_path': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else "/static/images/placeholder.jpg",
                        'backdrop_path': f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}" if movie.get('backdrop_path') else None,
                        'release_date': movie.get('release_date', 'Unknown'),
                        'vote_average': movie.get('vote_average', 0.0)
                    }
                    formatted_movies.append(formatted_movie)
                except Exception as e:
                    print(f"Error formatting movie: {e}")
                    continue
            
            return formatted_movies
        except Exception as e:
            print(f"Error searching movies: {e}")
            return []

    def search_series(self, query, page=1):
        try:
            url = f"{self.base_url}/search/tv"
            params = {
                'api_key': self.api_key,
                'query': query,
                'page': page,
                'language': 'en-US',
                'include_adult': False,
                'certification_country': 'US',
                'certification.lte': 'TV-PG'  # Using TV-PG rating for series
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error from TMDB API: {response.text}")
                return []
            
            data = response.json()
            formatted_series = []
            
            for series in data.get('results', []):
                try:
                    # Skip inappropriate content
                    if not self._is_appropriate_content({
                        'title': series.get('name', ''),
                        'overview': series.get('overview', '')
                    }):
                        print(f"Filtered out inappropriate series: {series.get('name', 'Unknown')}")
                        continue
                        
                    formatted_series_item = {
                        'id': series.get('id', 0),
                        'title': series.get('name', 'Unknown Title'),
                        'overview': series.get('overview', 'No overview available'),
                        'poster_path': f"https://image.tmdb.org/t/p/w500{series.get('poster_path')}" if series.get('poster_path') else "/static/images/placeholder.jpg",
                        'backdrop_path': f"https://image.tmdb.org/t/p/original{series.get('backdrop_path')}" if series.get('backdrop_path') else None,
                        'first_air_date': series.get('first_air_date', 'Unknown'),
                        'vote_average': series.get('vote_average', 0.0)
                    }
                    formatted_series.append(formatted_series_item)
                except Exception as e:
                    print(f"Error formatting series: {e}")
                    continue
            
            return formatted_series
        except Exception as e:
            print(f"Error searching series: {e}")
            return []

    def get_movies_by_genre(self, genre_id, page=1):
        try:
            url = f"{self.base_url}/discover/movie"
            params = {
                'api_key': self.api_key,
                'with_genres': genre_id,
                'page': page,
                'language': 'en-US',
                'include_adult': False,  # Explicitly exclude adult content
                'certification_country': 'US',
                'certification.lte': 'PG-13'  # Only include up to PG-13 rated content
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error from TMDB API: {response.text}")
                return []
            
            data = response.json()
            formatted_movies = []
            
            for movie in data.get('results', []):
                try:
                    # Skip inappropriate content
                    if not self._is_appropriate_content(movie):
                        print(f"Filtered out inappropriate movie: {movie.get('title', 'Unknown')}")
                        continue
                        
                    formatted_movie = {
                        'id': movie.get('id', 0),
                        'title': movie.get('title', 'Unknown Title'),
                        'overview': movie.get('overview', 'No overview available'),
                        'poster_path': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else "/static/images/placeholder.jpg",
                        'backdrop_path': f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}" if movie.get('backdrop_path') else None,
                        'release_date': movie.get('release_date', 'Unknown'),
                        'vote_average': movie.get('vote_average', 0.0)
                    }
                    formatted_movies.append(formatted_movie)
                except Exception as e:
                    print(f"Error formatting movie: {e}")
                    continue
            
            return formatted_movies
        except Exception as e:
            print(f"Error fetching movies by genre: {e}")
            return []

    def get_similar_movies(self, movie_id):
        try:
            url = f"{self.base_url}/movie/{movie_id}/similar"
            params = {
                'api_key': self.api_key,
                'language': 'en-US',
                'include_adult': False,  # Explicitly exclude adult content
                'certification_country': 'US',
                'certification.lte': 'PG-13'  # Only include up to PG-13 rated content
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error from TMDB API: {response.text}")
                return []
            
            data = response.json()
            formatted_movies = []
            
            for movie in data.get('results', []):
                try:
                    # Skip inappropriate content
                    if not self._is_appropriate_content(movie):
                        print(f"Filtered out inappropriate movie: {movie.get('title', 'Unknown')}")
                        continue
                        
                    formatted_movie = {
                        'id': movie.get('id', 0),
                        'title': movie.get('title', 'Unknown Title'),
                        'overview': movie.get('overview', 'No overview available'),
                        'poster_path': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else "/static/images/placeholder.jpg",
                        'backdrop_path': f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}" if movie.get('backdrop_path') else None,
                        'release_date': movie.get('release_date', 'Unknown'),
                        'vote_average': movie.get('vote_average', 0.0)
                    }
                    formatted_movies.append(formatted_movie)
                except Exception as e:
                    print(f"Error formatting movie: {e}")
                    continue
            
            return formatted_movies
        except Exception as e:
            print(f"Error fetching similar movies: {e}")
            return []

    def get_genres(self):
        return self.genre.movie_list()

    def _is_appropriate_content(self, movie):
        """Check if the movie content is appropriate."""
        # Check title and overview for inappropriate keywords
        if self.inappropriate_pattern.search(movie.get('title', '')) or \
           self.inappropriate_pattern.search(movie.get('overview', '')):
            return False
        return True

    def get_documentaries(self, page=1):
        try:
            url = f"{self.base_url}/discover/movie"
            params = {
                'api_key': self.api_key,
                'with_genres': self.DOCUMENTARY_GENRE_ID,
                'sort_by': 'popularity.desc',
                'page': page,
                'language': 'en-US',
                'include_adult': False,  # Explicitly exclude adult content
                'certification_country': 'US',
                'certification.lte': 'PG-13'  # Only include up to PG-13 rated content
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error from TMDB API: {response.text}")
                return []
                
            data = response.json()
            formatted_docs = []
            
            for movie in data.get('results', []):
                try:
                    # Skip inappropriate content
                    if not self._is_appropriate_content(movie):
                        print(f"Filtered out inappropriate content: {movie.get('title', 'Unknown')}")
                        continue
                        
                    formatted_doc = {
                        'id': movie.get('id', 0),
                        'title': movie.get('title', 'Unknown Title'),
                        'overview': movie.get('overview', 'No overview available'),
                        'poster_path': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else "/static/images/placeholder.jpg",
                        'backdrop_path': f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}" if movie.get('backdrop_path') else None,
                        'release_date': movie.get('release_date', 'Unknown'),
                        'vote_average': movie.get('vote_average', 0.0)
                    }
                    formatted_docs.append(formatted_doc)
                except Exception as e:
                    print(f"Error formatting documentary: {e}")
                    continue
            
            return formatted_docs
        except Exception as e:
            print(f"Error fetching documentaries: {e}")
            return []

    def get_documentary_details(self, documentary_id):
        try:
            movie = self.movie.details(documentary_id)
            
            # Check if the content is appropriate
            if not self._is_appropriate_content({
                'title': getattr(movie, 'title', ''),
                'overview': getattr(movie, 'overview', '')
            }):
                raise Exception("Content not appropriate")
                
            return self.get_movie_details(documentary_id)
        except Exception as e:
            print(f"Error in get_documentary_details: {e}")
            raise

    def get_trending_documentaries(self):
        try:
            url = f"{self.base_url}/discover/movie"
            params = {
                'api_key': self.api_key,
                'with_genres': self.DOCUMENTARY_GENRE_ID,
                'sort_by': 'popularity.desc',
                'page': 1,
                'language': 'en-US',
                'include_adult': False,  # Explicitly exclude adult content
                'certification_country': 'US',
                'certification.lte': 'PG-13'  # Only include up to PG-13 rated content
            }
            
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error from TMDB API: {response.text}")
                return []
                
            data = response.json()
            formatted_docs = []
            
            for movie in data.get('results', [])[:8]:
                try:
                    # Skip inappropriate content
                    if not self._is_appropriate_content(movie):
                        print(f"Filtered out inappropriate content: {movie.get('title', 'Unknown')}")
                        continue
                        
                    formatted_doc = {
                        'id': movie.get('id', 0),
                        'title': movie.get('title', 'Unknown Title'),
                        'overview': movie.get('overview', 'No overview available'),
                        'poster_path': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else "/static/images/placeholder.jpg",
                        'backdrop_path': f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}" if movie.get('backdrop_path') else None,
                        'release_date': movie.get('release_date', 'Unknown'),
                        'vote_average': movie.get('vote_average', 0.0)
                    }
                    formatted_docs.append(formatted_doc)
                except Exception as e:
                    print(f"Error formatting documentary: {e}")
                    continue
            
            return formatted_docs
        except Exception as e:
            print(f"Error fetching trending documentaries: {e}")
            return []

    def _format_movie(self, movie):
        try:
            return {
                'id': getattr(movie, 'id', 0),
                'title': getattr(movie, 'title', 'Unknown Title'),
                'overview': getattr(movie, 'overview', 'No overview available'),
                'poster_path': getattr(movie, 'poster_path', None),
                'backdrop_path': getattr(movie, 'backdrop_path', None),
                'release_date': getattr(movie, 'release_date', 'Unknown'),
                'vote_average': getattr(movie, 'vote_average', 0.0)
            }
        except Exception as e:
            print(f"Error formatting movie: {e}")
            return None

    def _format_series(self, series):
        return {
            'id': series.id,
            'name': series.name,
            'overview': series.overview,
            'poster_path': series.poster_path,
            'backdrop_path': series.backdrop_path,
            'first_air_date': getattr(series, 'first_air_date', None),
            'vote_average': series.vote_average
        }
